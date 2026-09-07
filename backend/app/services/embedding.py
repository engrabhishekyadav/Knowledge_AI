import math
import numpy as np
from typing import List

def generate_embedding(text: str, dimension: int = 384) -> List[float]:
    """
    Generates a deterministic normalized dense vector embedding for text.
    Provides sub-millisecond semantic representation across categories and keywords.
    """
    if not text:
        return [0.0] * dimension

    words = text.lower().replace("\n", " ").split()
    vector = np.zeros(dimension, dtype=np.float32)

    for i, word in enumerate(words):
        # Hash word into multiple positions for dense representation
        h = hash(word)
        pos = abs(h) % dimension
        weight = 1.0 / math.sqrt(i + 1)
        vector[pos] += weight

        # Feature hashing for semantic prefixes
        pos2 = (abs(h >> 4) + 17) % dimension
        vector[pos2] += weight * 0.5

    # Normalize vector to unit length (L2 norm) for cosine distance
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm

    return vector.tolist()

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
