import json
import logging
import httpx
from typing import AsyncGenerator, Optional
from app.core.config import settings

logger = logging.getLogger("knowledge_ai.agent.llm")

# Streaming timeout: connect fast (5s), generous read (60s) for large requests
STREAM_TIMEOUT = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)

async def stream_gemini_tokens(
    system_prompt: str,
    prompt: str,
    target_count: Optional[int] = None
) -> AsyncGenerator[str, None]:
    """
    Streams tokens from Google Gemini API via OpenAI-compatible endpoint.
    Tries primary Gemini model followed by configured fallback model.
    """
    gemini_key = getattr(settings, "GEMINI_API_KEY", "")
    if not gemini_key or gemini_key.startswith("your-"):
        return

    gemini_models = [
        getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash"),
        getattr(settings, "GEMINI_FALLBACK_MODEL", "gemini-3.6-flash")
    ]
    gemini_headers = {
        "Authorization": f"Bearer {gemini_key}",
        "Content-Type": "application/json"
    }
    gemini_token_limit = 8192

    for g_model in gemini_models:
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
        try:
            async with httpx.AsyncClient(timeout=STREAM_TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    f"{settings.GEMINI_BASE_URL}/chat/completions",
                    headers=gemini_headers,
                    json=payload
                ) as response:
                    if response.status_code == 200:
                        has_tokens = False
                        async for line in response.aiter_lines():
                            if line.startswith("data: ") and line != "data: [DONE]":
                                try:
                                    data_json = json.loads(line[6:])
                                    choice = data_json.get("choices", [{}])[0]
                                    finish_reason = choice.get("finish_reason")
                                    delta = choice.get("delta", {})
                                    content_piece = delta.get("content", "")
                                    if content_piece:
                                        has_tokens = True
                                        yield content_piece
                                    if finish_reason == "length":
                                        yield "\n\n*(Note: Response reached maximum length. Type 'continue' to receive any remaining items.)*"
                                except Exception:
                                    continue
                        if has_tokens:
                            return
                    else:
                        resp_text = await response.aread()
                        logger.warning(f"Google Gemini model {g_model} returned {response.status_code}: {resp_text[:100]}")
        except Exception as err:
            logger.warning(f"Google Gemini attempt with {g_model} failed ({type(err).__name__}: {err}).")

async def stream_openrouter_tokens(
    system_prompt: str,
    prompt: str,
    target_count: Optional[int] = None
) -> AsyncGenerator[str, None]:
    """
    Streams tokens from OpenRouter API as fallback.
    """
    api_key = settings.OPENROUTER_API_KEY
    if not api_key or api_key.startswith("your-"):
        return

    primary_model = settings.OPENROUTER_MODEL or "minimax/minimax-m3:free"
    fallback_model = settings.OPENROUTER_FALLBACK_MODEL or "nvidia/nemotron-3.5-lightning:free"
    models_to_try = [primary_model]
    if fallback_model and fallback_model != primary_model:
        models_to_try.append(fallback_model)

    openrouter_token_limit = 3800 if (target_count and target_count > 5) else 2500
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "KnowledgeAI Platform",
        "Content-Type": "application/json"
    }

    for target_model in models_to_try:
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
        try:
            async with httpx.AsyncClient(timeout=STREAM_TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status_code == 200:
                        has_tokens = False
                        async for line in response.aiter_lines():
                            if line.startswith("data: ") and line != "data: [DONE]":
                                try:
                                    data_json = json.loads(line[6:])
                                    delta = data_json.get("choices", [{}])[0].get("delta", {})
                                    content_piece = delta.get("content", "")
                                    if content_piece:
                                        has_tokens = True
                                        yield content_piece
                                except Exception:
                                    continue
                        if has_tokens:
                            return
                    else:
                        resp_text = await response.aread()
                        logger.warning(f"OpenRouter model {target_model} returned {response.status_code}: {resp_text[:100]}")
        except Exception as err:
            logger.warning(f"OpenRouter attempt with {target_model} failed ({type(err).__name__}: {err}).")

async def stream_live_llm_tokens(
    system_prompt: str,
    prompt: str,
    target_count: Optional[int] = None
) -> AsyncGenerator[str, None]:
    """
    Chains live LLM streaming attempts: Primary Google Gemini -> Secondary OpenRouter.
    Yields tokens if any live provider succeeds.
    """
    # 1. Primary: Google Gemini
    gemini_yielded = False
    async for token in stream_gemini_tokens(system_prompt, prompt, target_count):
        gemini_yielded = True
        yield token

    if gemini_yielded:
        return

    # 2. Secondary: OpenRouter
    openrouter_yielded = False
    async for token in stream_openrouter_tokens(system_prompt, prompt, target_count):
        openrouter_yielded = True
        yield token

    if openrouter_yielded:
        return
