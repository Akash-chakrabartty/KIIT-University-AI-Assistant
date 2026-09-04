import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from web.routes import router
from db import get_connection
from reasoning.llm_provider import GeminiProvider

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
def startup():
    db_path = os.getenv("DATABASE_PATH", "./data/university.db")
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    app.state.db = get_connection(db_path)

    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if api_key:
        app.state.llm_provider = GeminiProvider(api_key=api_key, model_name=model_name)
    else:
        # No key configured yet -- /api/chat will surface a clean "error"
        # status instead of crashing (Section 10).
        class _MissingKeyProvider:
            def generate(self, prompt: str) -> str:
                raise RuntimeError("GEMINI_API_KEY is not configured")
        app.state.llm_provider = _MissingKeyProvider()


# Run with: uvicorn main:app --reload --port 8080
