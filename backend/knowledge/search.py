"""Project responsibility: embeddings + semantic search."""
import numpy as np

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed(text: str) -> np.ndarray:
    return _get_model().encode(text)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def search(conn, query: str, top_k: int = 5) -> list[dict]:
    """Loads every chunk row, decodes its stored embedding, ranks by
    cosine similarity to the query, and returns the top_k as SearchResult
    dicts (Section 5's exact field set)."""
    query_vec = embed(query)
    rows = conn.execute(
        """SELECT passage_id, document_title, page, section, text,
                  academic_year, url, embedding
           FROM chunks WHERE embedding IS NOT NULL"""
    ).fetchall()

    scored = []
    for row in rows:
        vec = np.frombuffer(row["embedding"], dtype=np.float32)
        score = _cosine(query_vec, vec)
        scored.append((score, row))

    scored.sort(key=lambda t: t[0], reverse=True)

    results = []
    for score, row in scored[:top_k]:
        results.append({
            "passage_id": row["passage_id"],
            "text": row["text"],
            "score": round(score, 4),
            "document_title": row["document_title"],
            "page": row["page"],
            "section": row["section"],
            "academic_year": row["academic_year"],
            "url": row["url"],
        })
    return results
