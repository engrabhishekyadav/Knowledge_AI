"""
RAG (Retrieval-Augmented Generation) Subsystem Package.

Consolidates document semantic chunking, batch vector indexing,
hybrid dense/sparse retrieval with RRF fusion, and precision reranking.
"""

from .chunker import chunk_document_text
from .indexer import index_note_chunks, backfill_unembedded_chunks
from .retriever import (
    retrieve_relevant_chunks,
    retrieve_dense_candidates,
    retrieve_sparse_candidates,
    reciprocal_rank_fusion,
)
from .reranker import (
    filter_and_rerank_chunks,
    extract_query_terms,
    compute_lexical_alignment_score,
)

__all__ = [
    "chunk_document_text",
    "index_note_chunks",
    "backfill_unembedded_chunks",
    "retrieve_relevant_chunks",
    "retrieve_dense_candidates",
    "retrieve_sparse_candidates",
    "reciprocal_rank_fusion",
    "filter_and_rerank_chunks",
    "extract_query_terms",
    "compute_lexical_alignment_score",
]
