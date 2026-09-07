import json
import httpx
import logging
import asyncio
import re
from typing import AsyncGenerator, Dict, Any, Optional
from app.core.config import settings
from app.services.nlp_extractor import extract_tasks_from_text

logger = logging.getLogger("knowledge_ai.agent")

def generate_dynamic_fallback(prompt: str, active_note: Optional[Dict[str, Any]], is_interview: bool, is_summary: bool) -> str:
    """
    Generates a dynamic, document-grounded fallback response if external LLM APIs are offline.
    Extracts actual headings, keywords, and topics directly from the document.
    """
    if not active_note:
        return f"### Workspace Assistant\n\nI analyzed your query: **\"{prompt}\"**. Please select or upload a document to unlock deep contextual answers, question generation, and task extraction."

    title = active_note.get("title", "Active Document")
    content = active_note.get("content", "")
    
    # Extract headings and meaningful lines
    headings = re.findall(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)
    bullet_items = re.findall(r"^\s*[-*]\s+(.+)$", content, re.MULTILINE)
    
    # Clean text to extract keywords
    clean_words = re.findall(r"\b[A-Za-z]{4,}\b", content)
    stop_words = {"this", "that", "with", "from", "have", "were", "been", "will", "your", "more", "also", "into", "some", "document"}
    keywords = [w for w in clean_words if w.lower() not in stop_words]
    top_keywords = list(dict.fromkeys(keywords))[:8]

    if is_interview:
        q1_topic = headings[0] if headings else (top_keywords[0] if top_keywords else "Core Concepts")
        q2_topic = headings[1] if len(headings) > 1 else (top_keywords[1] if len(top_keywords) > 1 else "Implementation Details")
        
        return (
            f"## 🎯 Comprehensive Interview & Assessment Guide: *{title}*\n\n"
            f"Based on an in-depth review of **\"{title}\"**, here are tailored technical, conceptual, and practical questions:\n\n"
            f"### 1. Core Technical Question: {q1_topic}\n"
            f"**Q: Can you explain the fundamental principles and architecture behind {q1_topic} as detailed in this document?**\n\n"
            f"* **Detailed Model Answer**: Start by defining the primary objective and architectural trade-offs. Discuss how data flows through the system, the key components involved, and how performance and reliability are maintained.\n"
            f"* **Evaluation Criteria**: Depth of understanding, clarity in explaining complex trade-offs, and practical application.\n\n"
            f"### 2. Deep-Dive & Practical Scenario: {q2_topic}\n"
            f"**Q: How would you troubleshoot, optimize, or scale the processes outlined in {q2_topic} when facing real-world constraints?**\n\n"
            f"* **Detailed Model Answer**: Outline a systematic approach: identify bottlenecks using observability/metrics, evaluate caching or indexing options, and implement resilient error recovery mechanisms.\n"
            f"* **Key Discussion Points**: Scalability, fault tolerance, and code/system maintainability.\n\n"
            f"### 3. Behavioral & Situational Question (STAR Method)\n"
            f"**Q: Describe a scenario where you had to quickly master the subject matter in \"{title}\" to deliver a high-stakes project or solve an urgent blocker.**\n\n"
            f"* **Situation & Task**: Explain the initial problem, technical constraints, and deadline.\n"
            f"* **Action**: Detail the specific research, experimentation, and cross-team collaboration you undertook.\n"
            f"* **Result**: Quantify the positive outcome (improved efficiency, zero downtime, or team alignment).\n\n"
            f"### 💡 Key Focus Areas for Mastery\n"
            + "".join([f"- **{kw}**: Review core definitions and hands-on use cases.\n" for kw in top_keywords[:4]])
        )

    elif is_summary:
        key_points_str = "\n".join([f"- {item}" for item in bullet_items[:5]]) if bullet_items else "- Thorough analysis of core objectives and structured findings.\n- Detailed methodologies and implementation steps."
        return (
            f"## 📋 Comprehensive Executive Summary: *{title}*\n\n"
            f"### Document Overview\n"
            f"**\"{title}\"** provides detailed documentation covering domain concepts, practical workflows, and strategic guidelines.\n\n"
            f"### Key Highlights & Documented Takeaways\n"
            f"{key_points_str}\n\n"
            f"### Core Themes & Subject Areas\n"
            f"{', '.join(top_keywords) if top_keywords else 'Technical specifications and workflow documentation.'}\n\n"
            f"### Strategic Next Steps\n"
            f"1. Consolidate action items into active Kanban tasks.\n"
            f"2. Link related reference documents to expand semantic knowledge coverage."
        )
    else:
        relevant_extract = "\n".join(bullet_items[:4]) if bullet_items else content[:350].strip()
        return (
            f"### Document Insights on *\"{title}\"*\n\n"
            f"Regarding your query **\"{prompt}\"**, here is a detailed breakdown based on the document text:\n\n"
            f"```markdown\n{relevant_extract}\n```\n\n"
            f"**Key Analysis**:\n"
            f"- The document emphasizes: {', '.join(top_keywords[:5]) if top_keywords else 'Structured execution'}.\n"
            f"- For further exploration, you can ask for step-by-step procedures, technical comparisons, or actionable Kanban items."
        )


async def stream_agent_response(
    prompt: str,
    active_note: Optional[Dict[str, Any]] = None,
    note_context: str = ""
) -> AsyncGenerator[str, None]:
    """
    Streams agent tokens and action cards via Server-Sent Events (SSE).
    Uses high-speed primary LLM (MiniMax M3) with automatic fallback and universal document grounding.
    """
    api_key = settings.OPENROUTER_API_KEY
    primary_model = settings.OPENROUTER_MODEL or "minimax/minimax-m3:free"
    fallback_model = settings.OPENROUTER_FALLBACK_MODEL or "nvidia/nemotron-3.5-lightning:free"
    
    lower_prompt = prompt.lower()
    is_extract_query = any(w in lower_prompt for w in ["extract", "action item", "todo", "kanban task", "tasks from"])
    is_summarize_query = any(w in lower_prompt for w in ["summarize", "summary", "overview", "executive summary", "key takeaways"])
    is_interview_query = any(w in lower_prompt for w in ["interview", "question", "questions", "quiz", "prep", "test my", "mock", "practice"])

    actions = []
    
    # 1. NLP Task Extraction Action
    if is_extract_query and active_note:
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

    # 2. Universal Document Grounded System Prompt
    system_prompt = (
        "You are KnowledgeAI Copilot, an elite AI research assistant, technical mentor, and knowledge analyst.\n"
        "You have direct access to the user's active document and workspace context.\n\n"
        "CORE OPERATING PRINCIPLES:\n"
        "1. DEEP GROUNDING: Base your answers directly on the facts, terminology, data, and context in the active document. "
        "Cite relevant sections, concepts, and details from the document explicitly.\n"
        "2. THOROUGH & COMPREHENSIVE: Provide high-value, complete, and detailed answers ('good amount of answers'). "
        "Do not give superficial, generic, or brief one-line summaries. Explain the underlying 'Why' and 'How', outline practical implications, and use structured Markdown (bold concepts, bullet points, headers, tables, and code snippets where relevant).\n"
        "3. UNIVERSAL ADAPTABILITY: The active document may be ANY type of document — a Technical Specification, Academic/Research Paper, Resume/CV, Meeting Minutes, Architecture Document, Business Proposal, Study Guide, or Codebase. Adapt your terminology and analysis precisely to the document's domain.\n"
    )

    # Detect if user requested a specific quantity (e.g. "20 questions", "10 interview questions")
    count_match = re.search(r'\b(\d{1,2})\s+(?:questions|interview questions|items|points|topics)\b', lower_prompt)
    target_count = int(count_match.group(1)) if count_match else None

    if is_interview_query:
        if target_count:
            count_instruction = (
                f"STRICT USER QUANTITY & COMPLETION REQUIREMENT: The user explicitly requested {target_count} questions. "
                f"You MUST generate ALL {target_count} numbered questions (from Question 1 to Question {target_count}) without stopping early. "
                f"Keep each model answer high-yield, structured, and focused (2-3 concise bullet points or a short, clean code snippet) so that ALL {target_count} questions fit completely without cutting off."
            )
        else:
            count_instruction = (
                "Generate 6 to 8 targeted, high-yield questions with clear, structured model answers. "
                "Keep each model answer focused and structured so the entire assessment completes cleanly without cutting off."
            )

        system_prompt += (
            f"\nQUESTION GENERATION & DEEP ASSESSMENT MODE:\n"
            f"{count_instruction}\n"
            "Analyze the active document thoroughly and generate targeted, challenging, highly relevant questions:\n"
            "- For EACH question, provide an informative, clear MODEL ANSWER that directly explains the concept.\n"
            "- When providing code examples, keep them concise and focused on the core pattern rather than bloated boilerplate.\n"
            "- If the document is a Resume/CV: generate technical questions based on their specific skills/projects, plus situational/behavioral questions tailored to their stated experience.\n"
            "- If the document is a Technical/Business/Academic document: generate conceptual, architectural, and problem-solving questions testing deep understanding of the document's core thesis and implementation.\n"
            "- Conclude with a clean Preparation Checklist or key takeaways so the response finishes completely."
        )
    elif is_summarize_query:
        system_prompt += (
            "\nEXECUTIVE ANALYSIS & SUMMARY MODE:\n"
            "Provide a comprehensive, structured breakdown of the active document:\n"
            "- Executive Overview & Core Objective\n"
            "- Critical Concepts, Data & Findings\n"
            "- Technical / Strategic Analysis\n"
            "- Actionable Insights & Key Takeaways\n"
            "Ensure the summary is thorough and captures all essential details."
        )
    else:
        system_prompt += (
            "\nANSWERING QUESTIONS:\n"
            "Answer the user's query thoroughly using the provided document context. If the query asks for solutions, explanations, comparisons, or recommendations, provide rich, well-reasoned answers with concrete details from the document."
        )

    if active_note:
        doc_title = active_note.get("title", "Untitled Document")
        doc_category = active_note.get("category", "General")
        doc_tags = ", ".join(active_note.get("tags", []))
        doc_content = active_note.get("content", "")
        system_prompt += (
            f"\n\n--- ACTIVE DOCUMENT CONTEXT ---\n"
            f"Title: {doc_title}\n"
            f"Category: {doc_category}\n"
            f"Tags: {doc_tags}\n\n"
            f"Document Content:\n{doc_content}\n"
            f"--- END DOCUMENT CONTEXT ---"
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "KnowledgeAI Platform",
        "Content-Type": "application/json"
    }

    models_to_try = [primary_model]
    if fallback_model and fallback_model != primary_model:
        models_to_try.append(fallback_model)

    used_live_api = False
    full_text_accumulated = ""

    # Streaming timeout: connect fast (5s), generous read (60s) for large counts (e.g. 20 questions)
    stream_timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
    # Gemini supports up to 8192 output tokens; OpenRouter free tier is capped lower
    gemini_token_limit = 8192
    openrouter_token_limit = 3800 if (target_count and target_count > 5) else 2500

    # 1. Primary: Google Gemini API (ultra-fast ~1.6s response, up to 8192 tokens)
    gemini_key = getattr(settings, "GEMINI_API_KEY", "")
    if gemini_key and not gemini_key.startswith("your-"):
        gemini_models = [
            getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash"),
            getattr(settings, "GEMINI_FALLBACK_MODEL", "gemini-3.6-flash")
        ]
        gemini_headers = {
            "Authorization": f"Bearer {gemini_key}",
            "Content-Type": "application/json"
        }
        for g_model in gemini_models:
            if used_live_api:
                break
            try:
                payload = {
                    "model": g_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": True,
                    "temperature": 0.35,
                    "max_tokens": gemini_token_limit
                }
                logger.info(f"Connecting to Google Gemini stream with model: {g_model}")
                async with httpx.AsyncClient(timeout=stream_timeout) as client:
                    async with client.stream(
                        "POST",
                        f"{settings.GEMINI_BASE_URL}/chat/completions",
                        headers=gemini_headers,
                        json=payload
                    ) as response:
                        if response.status_code == 200:
                            used_live_api = True
                            async for line in response.aiter_lines():
                                if line.startswith("data: ") and line != "data: [DONE]":
                                    try:
                                        data_json = json.loads(line[6:])
                                        choice = data_json.get("choices", [{}])[0]
                                        finish_reason = choice.get("finish_reason")
                                        delta = choice.get("delta", {})
                                        content_piece = delta.get("content", "")
                                        if content_piece:
                                            full_text_accumulated += content_piece
                                            yield f"data: {json.dumps({'type': 'token', 'content': content_piece})}\n\n"
                                        if finish_reason == "length":
                                            continue_hint = "\n\n*(Note: Response reached maximum length. Type 'continue' to receive any remaining items.)*"
                                            yield f"data: {json.dumps({'type': 'token', 'content': continue_hint})}\n\n"
                                    except Exception:
                                        continue
                            logger.info(f"Successfully streamed {len(full_text_accumulated)} chars using Gemini {g_model}")
                            break
                        else:
                            resp_text = await response.aread()
                            logger.warning(f"Google Gemini model {g_model} returned {response.status_code}: {resp_text[:100]}")
            except Exception as err:
                logger.warning(f"Google Gemini attempt with {g_model} failed ({type(err).__name__}: {err}).")

    # 2. Secondary: OpenRouter API (fallback if Gemini was not used or failed)
    if not used_live_api and api_key and not api_key.startswith("your-"):
        for target_model in models_to_try:
            if used_live_api:
                break
            try:
                payload = {
                    "model": target_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": True,
                    "temperature": 0.35,
                    "max_tokens": openrouter_token_limit
                }

                logger.info(f"Connecting to OpenRouter stream with model: {target_model}")
                async with httpx.AsyncClient(timeout=stream_timeout) as client:
                    async with client.stream(
                        "POST",
                        f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status_code == 200:
                            used_live_api = True
                            async for line in response.aiter_lines():
                                if line.startswith("data: ") and line != "data: [DONE]":
                                    try:
                                        data_json = json.loads(line[6:])
                                        delta = data_json.get("choices", [{}])[0].get("delta", {})
                                        content_piece = delta.get("content", "")
                                        if content_piece:
                                            full_text_accumulated += content_piece
                                            yield f"data: {json.dumps({'type': 'token', 'content': content_piece})}\n\n"
                                    except Exception:
                                        continue
                            logger.info(f"Successfully streamed {len(full_text_accumulated)} chars using {target_model}")
                            break
                        else:
                            resp_text = await response.aread()
                            logger.warning(f"OpenRouter model {target_model} returned {response.status_code}: {resp_text[:100]}")
            except Exception as err:
                logger.warning(f"OpenRouter attempt with {target_model} failed ({type(err).__name__}: {err}).")

    # 3. Dynamic Context-Aware Fallback (if external APIs unavailable)
    if not used_live_api:
        logger.info("Using dynamic local fallback generator grounded in active document text.")
        fallback_msg = generate_dynamic_fallback(prompt, active_note, is_interview_query, is_summarize_query)
        
        if is_interview_query and active_note:
            actions.append({
                "type": "INSERT_SUMMARY",
                "label": "Insert Prep Guide into Note",
                "payload": f"\n\n---\n{fallback_msg}\n"
            })
        elif is_summarize_query and active_note:
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

    # 4. Emit Action Cards if any
    if actions:
        for action in actions:
            yield f"data: {json.dumps({'type': 'action', 'action': action})}\n\n"

    # End of stream event
    yield "data: [DONE]\n\n"
