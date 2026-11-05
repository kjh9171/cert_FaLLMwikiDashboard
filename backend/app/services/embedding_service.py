import math
import hashlib
import json
from typing import List

def generate_pseudo_embedding(text: str, dim: int = 1536) -> List[float]:
    """
    텍스트에 대한 1536차원 정규화 임베딩 벡터 생성.
    Ollama나 외부 임베딩 서버가 부재해도 즉시 작동하는 견고한 해시 기반 벡터 임베딩.
    """
    cleaned = text.strip().lower()
    vec = []
    
    # Generate deterministic pseudo-random float vector from text hash seeds
    for i in range(dim):
        seed_str = f"{cleaned}:{i}"
        h = hashlib.sha256(seed_str.encode('utf-8')).hexdigest()
        val = (int(h[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0
        vec.append(val)
        
    # Normalize vector to unit length (L2 norm = 1.0) for Cosine Similarity
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """두 벡터 간의 코사인 유사도 (-1.0 ~ 1.0) 계산"""
    if len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def chunk_markdown_text(text: str, max_chunk_size: int = 500) -> List[str]:
    """문서를 의미 단위(단락 또는 줄)로 분할"""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        para_clean = para.strip()
        if not para_clean:
            continue
        if current_len + len(para_clean) > max_chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para_clean]
            current_len = len(para_clean)
        else:
            current_chunk.append(para_clean)
            current_len += len(para_clean)

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    return chunks if chunks else [text]

