"""Member 1 responsibility: document ingestion, extraction, chunking."""
import re
import fitz  # PyMuPDF
import requests


def download(url: str, dest_path: str) -> bool:
    """Fetch `url` and save it to `dest_path`. Returns False (not an
    exception) on timeout/404/connection error so ingestion can skip a
    bad source and keep going."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        return True
    except requests.RequestException:
        return False


def extract_pages(pdf_path: str) -> list[tuple[int, str]]:
    """Returns [(page_no, page_text), ...], 1-indexed pages."""
    doc = fitz.open(pdf_path)
    return [(page_no, page.get_text("text")) for page_no, page in enumerate(doc, 1)]


def make_chunks(text: str, max_chars: int = 1200) -> list[str]:
    """Split `text` into paragraphs, then group paragraphs into chunks
    no longer than max_chars. Returns a list of chunk strings."""
    # Split on blank lines / paragraph breaks; fall back to single newlines
    # if the page has no blank-line separation (common with PDF extraction).
    raw_paragraphs = re.split(r"\n\s*\n", text.strip())
    paragraphs = []
    for p in raw_paragraphs:
        p = p.strip()
        if not p:
            continue
        # A page that came out as one giant blob: split on sentence-ish
        # boundaries instead so we don't produce a single huge paragraph.
        if len(p) > max_chars * 2 and "\n\n" not in p:
            sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", p)
            paragraphs.extend(s.strip() for s in sentences if s.strip())
        else:
            paragraphs.append(p)

    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        candidate = (current + "\n\n" + para).strip() if current else para
        if len(candidate) > max_chars and current:
            chunks.append(current.strip())
            current = para
        else:
            current = candidate
    if current.strip():
        chunks.append(current.strip())

    # Guard: an empty/near-empty page (e.g. scanned image) yields no chunks.
    return [c for c in chunks if len(c.strip()) >= 20]


def save_chunk(conn, passage_id, document_id, document_title, page, section,
               text, academic_year, url, embedding):
    conn.execute(
        """INSERT OR REPLACE INTO chunks
           (passage_id, document_id, document_title, page, section, text,
            academic_year, url, embedding)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (passage_id, document_id, document_title, page, section, text,
         academic_year, url, embedding),
    )
    conn.commit()


def save_document(conn, document_id, title, url, academic_year, status="active"):
    conn.execute(
        """INSERT OR REPLACE INTO documents
           (document_id, title, url, academic_year, status)
           VALUES (?, ?, ?, ?, ?)""",
        (document_id, title, url, academic_year, status),
    )
    conn.commit()


def ingest_document(conn, pdf_path: str, document_id: str, document_title: str,
                     academic_year: str, url: str, embed_fn=None) -> int:
    """Runs extract_pages -> make_chunks -> save_chunk for every page of
    one already-downloaded PDF. Returns the number of chunks saved.
    If `embed_fn` is given, each chunk's embedding is computed and stored
    at ingestion time (Section 5) instead of left None."""
    save_document(conn, document_id, document_title, url, academic_year)
    total = 0
    for page_no, page_text in extract_pages(pdf_path):
        if not page_text or not page_text.strip():
            # Likely a scanned page with no extractable text -- flag and skip.
            continue
        for i, chunk_text in enumerate(make_chunks(page_text), start=1):
            passage_id = f"{document_id}-P{page_no}-C{i:02d}"
            embedding = embed_fn(chunk_text) if embed_fn else None
            if embedding is not None:
                embedding = embedding.astype("float32").tobytes()
            save_chunk(conn, passage_id, document_id, document_title, page_no,
                       section=None, text=chunk_text, academic_year=academic_year,
                       url=url, embedding=embedding)
            total += 1
    return total
