"""
KnowledgeAI Agent Service Package.
Decomposed into single-responsibility modules:
- prompts: Intent classification and system prompt construction with prompt-injection defense.
- llm: Google Gemini and OpenRouter streaming HTTP clients.
- fallback: Offline dynamic document-grounded response synthesis.
- orchestrator: High-level streaming coordinator and SSE formatter.
"""

from .orchestrator import stream_agent_response
from .fallback import generate_dynamic_fallback
from .prompts import classify_agent_intent, build_system_prompt
from .llm import stream_live_llm_tokens, stream_gemini_tokens, stream_openrouter_tokens

__all__ = [
    "stream_agent_response",
    "generate_dynamic_fallback",
    "classify_agent_intent",
    "build_system_prompt",
    "stream_live_llm_tokens",
    "stream_gemini_tokens",
    "stream_openrouter_tokens"
]
