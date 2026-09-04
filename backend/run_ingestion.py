"""Exact ingestion command: python run_ingestion.py

Reads backend/data/sources.json (a list of {document_id, title, path,
academic_year, url} entries pointing at PDFs already placed in
backend/data/raw/) and ingests each one: extract -> chunk -> embed -> store.
"""
import json
import os
from db import get_connection
from knowledge.ingest import ingest_document
from knowledge.search import embed

SOURCES_FILE = os.path.join(os.path.dirname(__file__), "data", "sources.json")
DB_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "data", "university.db"))


def main():
    if not os.path.exists(SOURCES_FILE):
        print(f"No sources file found at {SOURCES_FILE}. See data/sources.json.example.")
        return

    with open(SOURCES_FILE) as f:
        sources = json.load(f)

    conn = get_connection(DB_PATH)
    total_chunks = 0
    for src in sources:
        pdf_path = os.path.join(os.path.dirname(__file__), "data", "raw", src["filename"])
        if not os.path.exists(pdf_path):
            print(f"SKIP {src['document_id']}: file not found at {pdf_path}")
            continue
        n = ingest_document(
            conn,
            pdf_path=pdf_path,
            document_id=src["document_id"],
            document_title=src["title"],
            academic_year=src.get("academic_year", ""),
            url=src.get("url", ""),
            embed_fn=embed,
        )
        print(f"OK {src['document_id']}: {n} chunks")
        total_chunks += n

    print(f"Ingestion complete. {total_chunks} chunks total in {DB_PATH}")


if __name__ == "__main__":
    main()
