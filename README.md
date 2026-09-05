# KIIT University AI Assistant — Project Implementation


<img width="1917" height="1015" alt="image" src="https://github.com/user-attachments/assets/3765c2ee-a170-42f5-b1a9-b8014d606378" />


<img width="1914" height="1014" alt="image" src="https://github.com/user-attachments/assets/36dc4702-6781-4031-a321-e92acfcae5bb" />




Grounded RAG assistant for KIIT University information. This repo implements
**Project (Knowledge module: ingestion, chunking, embeddings, search)** and
**Project (Reasoning module: RAG pipeline, citation verification, rules,
web API)**, wired together end-to-end.



## 1. Requirements
- Python 3.11+
- Node 18+
- A Gemini API key (https://aistudio.google.com/apikey)

## 2. Install
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install
```

## 3. Configure
```bash
cd backend
cp .env.example .env
# edit .env and set GEMINI_API_KEY
```

## 4. Prepare the KIIT PDF data
Place your KIIT PDFs in `backend/data/raw/` (filenames matching
`backend/data/sources.json.example`), then:
```bash
cp backend/data/sources.json.example backend/data/sources.json
```
Edit `sources.json` if your filenames differ.

## 5. Ingest
```bash
cd backend
python run_ingestion.py
```

## 6. Start the backend
```bash
cd backend
uvicorn main:app --reload --port 8080
```

## 7. Start the frontend
```bash
cd frontend
npm run dev
```
Open http://localhost:5173

## 8. Run tests
```bash
cd backend
python -m pytest tests/ -v
```
19 tests currently pass, covering chunking, citation verification, the
calculation-routing path, and error handling. These do not require a
Gemini key or network access.

## 9. Example question
"Can I improve my CGPA?" → cites the grade-improvement registration rule
(R.13 in the SCE Student Handbook) with page/section and a status of
`verified`.

## 10. Verifying citations
Every `passage_id` shown to the user is checked against the actual
retrieved evidence in `verify_citations()` (`reasoning/pipeline.py`) —
a citation the model invents that isn't in the retrieved set is dropped,
never shown.

## Common errors and fixes
| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: fitz` | `pip install pymupdf` (package name differs from import name) |
| `/api/chat` returns `status: "error"` | Check `GEMINI_API_KEY` is set in `backend/.env` |
| No results / empty `cannot_verify` on everything | Run `python run_ingestion.py` — the DB has no chunks yet |
| CORS error in browser console | Confirm frontend is running on port 5173 (matches `main.py`'s CORS config) |

## Status / what's verified vs. what needs you
- ✅ Chunking, citation verification, SGPA/eligibility rules, calculation
  routing, error handling: all covered by passing automated tests.
- ⚠️ Live ingestion against your real PDFs and live Gemini calls have
  **not** been run end-to-end in this environment — I don't have your
  actual PDF binaries on disk here (only their extracted text) or a
  Gemini key. Run steps 4–7 yourself to confirm those.
