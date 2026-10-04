import math
import logging
import asyncio
import hashlib
import numpy as np
import httpx
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger("knowledge_ai.embedding")

def generate_fallback_embedding(text: str, dimension: int = settings.VECTOR_DIMENSION) -> List[float]:
    """
    Deterministic normalized dense vector fallback using NumPy feature hashing with SHA-256.
    Runs locally in sub-milliseconds without network dependencies and stays stable across restarts.
    """
    if not text:
        return [0.0] * dimension

    words = text.lower().replace("\n", " ").split()
    vector = np.zeros(dimension, dtype=np.float32)

    for i, word in enumerate(words):
        # Use deterministic SHA-256 instead of Python's randomized hash()
        digest = hashlib.sha256(word.encode("utf-8")).digest()
        h = int.from_bytes(digest[:8], byteorder="big", signed=False)
        pos = h % dimension
        weight = 1.0 / math.sqrt(i + 1)
        vector[pos] += weight

        pos2 = ((h >> 4) + 17) % dimension
        vector[pos2] += weight * 0.5

    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm

    return vector.tolist()

async def generate_dense_embedding(
    text: str,
    dimension: int = settings.VECTOR_DIMENSION,
    max_retries: int = 3
) -> Optional[List[float]]:
    """
    Generates a dense neural vector embedding via Google Gemini Embedding API (text-embedding-004).
    Includes automatic exponential backoff retry for transient 429/503 errors.
    Returns None if external API is unconfigured or unavailable, rather than corrupting the vector store
    with pseudo-random hash vectors.
    """
    if not text or not text.strip():
        return [0.0] * dimension

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.debug("No GEMINI_API_KEY configured. Returning None (safe lexical fallback mode).")
        return None

    primary_model = getattr(settings, "GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    candidate_models = [primary_model]
    for alt in ["gemini-embedding-001", "gemini-embedding-2", "text-embedding-004"]:
        if alt not in candidate_models:
            candidate_models.append(alt)

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "content": {"parts": [{"text": text[:2048]}]},
        "outputDimensionality": dimension
    }

    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:embedContent"
        model_failed_404 = False
        for attempt in range(1, max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        values = data.get("embedding", {}).get("values", [])
                        if len(values) == dimension:
                            return values
                        elif values:
                            # Pad or truncate if dimensions differ
                            if len(values) < dimension:
                                values = values + [0.0] * (dimension - len(values))
                            else:
                                values = values[:dimension]
                            return values
                    elif res.status_code == 404:
                        logger.debug(f"Gemini model '{model_name}' not available (404). Trying next candidate...")
                        model_failed_404 = True
                        break
                    elif res.status_code in (429, 503) and attempt < max_retries:
                        backoff = (0.5 * (2 ** (attempt - 1))) + (0.1 * attempt)
                        logger.warning(
                            f"Gemini embedding API rate-limited / busy ({res.status_code}). Retrying in {backoff:.2f}s "
                            f"(attempt {attempt}/{max_retries})..."
                        )
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        logger.warning(f"Gemini embedding API ({model_name}) returned status {res.status_code}: {res.text[:120]}")
                        break
            except (httpx.RequestError, httpx.TimeoutException) as req_err:
                if attempt < max_retries:
                    backoff = (0.5 * (2 ** (attempt - 1)))
                    logger.warning(f"Gemini embedding network glitch ({req_err}). Retrying in {backoff:.2f}s...")
                    await asyncio.sleep(backoff)
                    continue
                else:
                    logger.warning(f"Gemini embedding API request failed after {max_retries} attempts: {req_err}")
            except Exception as e:
                logger.warning(f"Unexpected error in generate_dense_embedding: {e}")
                break

        if not model_failed_404:
            break

    return None

async def batch_generate_embeddings(
    texts: List[str],
    dimension: int = settings.VECTOR_DIMENSION,
    concurrency: int = 5
) -> List[Optional[List[float]]]:
    """
    Generates embeddings for multiple text chunks concurrently with controlled concurrency.
    Returns None for any chunks where the embedding could not be generated.
    """
    if not texts:
        return []

    semaphore = asyncio.Semaphore(concurrency)

    async def embed_with_limit(t: str) -> Optional[List[float]]:
        async with semaphore:
            return await generate_dense_embedding(t, dimension)

    tasks = [embed_with_limit(t) for t in texts]
    return await asyncio.gather(*tasks)

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates cosine similarity between two unit vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
