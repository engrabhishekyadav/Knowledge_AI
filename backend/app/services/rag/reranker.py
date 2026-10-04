import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("knowledge_ai.rag.reranker")

# Default stop words to exclude from lexical term alignment
COMMON_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
    "which", "this", "that", "these", "those", "then", "just", "so", "than",
    "such", "both", "through", "about", "for", "is", "of", "while", "during",
    "to", "from", "in", "out", "on", "off", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "s", "t",
    "can", "will", "don", "should", "now", "are", "was", "were", "been",
    "have", "has", "had", "having", "do", "does", "did", "doing", "would",
    "could", "be", "with", "into", "at", "by", "i", "you", "he", "she",
    "we", "they", "it", "my", "your", "their", "our", "his", "her", "its"
}

def extract_query_terms(query: str) -> List[str]:
    """Extracts non-stopword tokens from the query, truncated to 500 chars for safety."""
    safe_query = (query or "")[:500]
    words = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", safe_query.lower())
    return [w for w in words if w not in COMMON_STOP_WORDS]

def compute_lexical_alignment_score(query_terms: List[str], chunk_content: str, section: str = "") -> float:
    """
    Computes a normalized lexical alignment score (0.0 - 1.0) based on:
    - Term coverage: percentage of query terms present in the chunk.
    - Section heading match: bonus if query terms appear in the section heading.
    - Exact sub-phrase occurrence bonus.
    """
    if not query_terms:
        return 0.0

    content_lower = chunk_content.lower()
    section_lower = section.lower() if section else ""

    # Term presence
    matched_terms = [t for t in query_terms if t in content_lower]
    term_coverage = len(matched_terms) / len(query_terms)

    # Section relevance bonus
    section_matches = [t for t in query_terms if t in section_lower]
    section_bonus = 0.20 if section_matches else 0.0

    # Multi-term phrase bonus
    phrase_bonus = 0.0
    if len(query_terms) >= 2:
        phrase = " ".join(query_terms[:3])
        if phrase in content_lower:
            phrase_bonus = 0.15

    total_score = min(1.0, (term_coverage * 0.70) + section_bonus + phrase_bonus)
    return round(total_score, 4)

def filter_and_rerank_chunks(
    query: str,
    candidate_chunks: List[Dict[str, Any]],
    min_similarity: float = 0.40,
    top_k: int = 4
) -> Dict[str, Any]:
    """
    Applies noise-cutoff threshold filtering and precision cross-scoring reranking:
    1. Threshold Gate: Prunes candidates with low semantic cosine similarity and zero lexical hit.
       If the best candidate fails minimum threshold, flags has_relevant_context = False.
    2. Precision Reranker: Scores surviving candidates using a hybrid weighted blend:
       - 45% Dense Semantic Cosine Similarity
       - 35% Lexical Query Term Alignment (Exact match, section bonus, keyword density)
       - 20% Reciprocal Rank Fusion (RRF) rank score
    3. Returns the top-k highest quality chunks and context relevance status.
    """
    if not candidate_chunks:
        return {
            "chunks": [],
            "has_relevant_context": False,
            "best_score": 0.0,
            "total_candidates": 0
        }

    query_terms = extract_query_terms(query)
    surviving_candidates: List[Dict[str, Any]] = []

    # Maximum RRF score among candidates for normalization
    max_rrf = max((c.get("rrf_score", 0.0) for c in candidate_chunks), default=1.0)
    if max_rrf <= 0:
        max_rrf = 1.0

    for chunk in candidate_chunks:
        dense_sim = float(chunk.get("similarity_score", 0.0))
        rrf_score = float(chunk.get("rrf_score", 0.0))
        content = chunk.get("content", "")
        section = chunk.get("section", "")

        lexical_score = compute_lexical_alignment_score(query_terms, content, section)
        normalized_rrf = min(1.0, rrf_score / max_rrf) if max_rrf > 0 else 0.0

        # Precision Reranking Formula:
        # 45% Dense Similarity + 35% Lexical Alignment + 20% Normalized RRF
        rerank_score = round(
            (0.45 * dense_sim) +
            (0.35 * lexical_score) +
            (0.20 * normalized_rrf),
            4
        )

        # Threshold evaluation:
        # A candidate is deemed relevant if:
        # a) Strong lexical match: lexical_score >= 0.35 or combined
        # b) Combined semantic & lexical support: dense_sim >= min_similarity and lexical_score > 0.0
        # c) Pure semantic paraphrase: dense_sim >= max(min_similarity + 0.12, 0.52)
        if lexical_score >= 0.35 or (lexical_score >= 0.25 and dense_sim >= 0.20):
            is_relevant = True
        elif dense_sim >= min_similarity and lexical_score > 0.0:
            is_relevant = True
        elif dense_sim >= max(min_similarity + 0.12, 0.52):
            is_relevant = True
        else:
            is_relevant = False

        chunk_copy = dict(chunk)
        chunk_copy["lexical_score"] = lexical_score
        chunk_copy["rerank_score"] = rerank_score
        chunk_copy["is_relevant"] = is_relevant

        if is_relevant:
            surviving_candidates.append(chunk_copy)

    # Sort surviving candidates by rerank_score descending
    surviving_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

    has_context = len(surviving_candidates) > 0
    best_score = surviving_candidates[0]["rerank_score"] if has_context else (
        candidate_chunks[0].get("similarity_score", 0.0) if candidate_chunks else 0.0
    )

    final_chunks = surviving_candidates[:top_k]

    logger.info(
        f"Reranking complete: {len(candidate_chunks)} candidates -> "
        f"{len(surviving_candidates)} passed threshold (min_sim={min_similarity}) -> "
        f"returning top {len(final_chunks)} chunks (has_context={has_context}, best_score={best_score})"
    )

    return {
        "chunks": final_chunks,
        "has_relevant_context": has_context,
        "best_score": best_score,
        "total_candidates": len(candidate_chunks),
        "passed_threshold_count": len(surviving_candidates)
    }
