"""
GraphTriage — Sentence-BERT Embedding Module (Day 4, Step 1)

Wraps the Sentence-Transformers model used to convert ticket text into
dense vector embeddings, per architecture.md Section 4 / design.md Section 3.1.

This module is shared by:
  - training/generate_embeddings.py (offline, Day 4) - embeds the whole dataset
  - the live FastAPI app (from Day 7 onward) - embeds a single new ticket at
    prediction time

The model is downloaded once (from Hugging Face) the first time this runs on
a machine with internet access, then cached locally — subsequent runs are
fast and don't need the internet.
"""

from functools import lru_cache

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


@lru_cache(maxsize=1)
def get_model():
    """Load (and cache in-process) the Sentence-BERT model, so repeated
    calls within the same run don't reload it from disk each time."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts):
    """
    texts: list[str]
    returns: numpy.ndarray of shape (len(texts), EMBEDDING_DIM)
    """
    model = get_model()
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)


def embed_single(text):
    """Convenience wrapper for embedding one piece of text (used later at
    prediction time for a single incoming ticket)."""
    return embed_texts([text])[0]
