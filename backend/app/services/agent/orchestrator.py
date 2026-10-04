import json
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional

from app.services.nlp_extractor import extract_tasks_from_text
from .prompts import classify_agent_intent, build_system_prompt
from .llm import stream_live_llm_tokens
from .fallback import generate_dynamic_fallback

logger = logging.getLogger("knowledge_ai.agent.orchestrator")

async def stream_agent_response(
    prompt: str,
    active_note: Optional[Dict[str, Any]] = None,
    note_context: str = "",
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None,
    has_relevant_context: bool = True
) -> AsyncGenerator[str, None]:
    """
    Streams agent tokens and action cards via Server-Sent Events (SSE).
    Uses high-speed primary LLM (Google Gemini / OpenRouter) with automatic fallback
    and hybrid document grounding.
    """
    # 1. Intent classification
    intent = classify_agent_intent(prompt)
    is_extract = intent["is_extract"]
    is_summary = intent["is_summary"]
    is_interview = intent["is_interview"]
    target_count = intent["target_count"]

    actions = []

    # 2. NLP Task Extraction Action
    if is_extract and active_note:
        extracted = extract_tasks_from_text(
            active_note.get("content", ""),
            active_note.get("id"),
            active_note.get("title")
        )
        if extracted:
            actions.append({
                "type": "ADD_TASKS",
                "label": f"Add {len(extracted)} extracted tasks to Kanban",
                "payload": extracted
            })

    # 3. Build hardened, document-grounded system prompt
    system_prompt = build_system_prompt(
        prompt=prompt,
        active_note=active_note,
        retrieved_chunks=retrieved_chunks,
        has_relevant_context=has_relevant_context,
        is_interview=is_interview,
        is_summary=is_summary,
        target_count=target_count
    )

    used_live_api = False
    full_text_accumulated = ""

    # 4. Stream tokens from Live LLM Providers (Gemini -> OpenRouter)
    async for token in stream_live_llm_tokens(system_prompt, prompt, target_count):
        used_live_api = True
        full_text_accumulated += token
        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

    # 5. Dynamic Context-Aware Fallback (if external APIs unavailable or offline)
    if not used_live_api:
        logger.info("External LLM unavailable. Using dynamic local fallback generator grounded in active document text.")
        fallback_msg = generate_dynamic_fallback(
            prompt=prompt,
            active_note=active_note,
            is_interview=is_interview,
            is_summary=is_summary,
            has_relevant_context=has_relevant_context
        )

        if is_interview and active_note:
            actions.append({
                "type": "INSERT_SUMMARY",
                "label": "Insert Prep Guide into Note",
                "payload": f"\n\n---\n{fallback_msg}\n"
            })
        elif is_summary and active_note:
            actions.append({
                "type": "INSERT_SUMMARY",
                "label": "Insert Summary into Note",
                "payload": f"\n\n---\n{fallback_msg}\n"
            })

        words = fallback_msg.split(" ")
        for i, word in enumerate(words):
            piece = (" " if i > 0 else "") + word
            yield f"data: {json.dumps({'type': 'token', 'content': piece})}\n\n"
            await asyncio.sleep(0.012)

    # 6. Emit Action Cards if any
    if actions:
        for action in actions:
            yield f"data: {json.dumps({'type': 'action', 'action': action})}\n\n"

    # 7. End of stream event
    yield "data: [DONE]\n\n"
