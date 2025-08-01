# backend/app/utils/embedding.py

from sentence_transformers import SentenceTransformer
from typing import List
import logging

# Initialize once
model = SentenceTransformer("BAAI/bge-base-en-v1.5")

# Optional: Log model load
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


def get_embedding(text: str) -> List[float]:
    """
    Generates a dense vector embedding for a given input text.
    Automatically prepends instruction for BGE model.
    """
    if not text.strip():
        return [0.0] * 768  # Return dummy vector for empty input

    prompt = f"Represent this sentence for retrieval: {text}"
    embedding = model.encode(prompt, normalize_embeddings=True)
    return embedding.tolist()
