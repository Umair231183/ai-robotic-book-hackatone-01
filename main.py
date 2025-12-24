from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from contextlib import asynccontextmanager

# -------------------------------------------------------------------
# Load .env ONLY in local development (never rely on it in production)
# -------------------------------------------------------------------
if os.getenv("ENV") != "production":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass


# -------------------------------------------------------------------
# FastAPI Lifespan (Startup / Shutdown)
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Import services here (NOT at module level)
        from src.services.db_service import NeonDBService
        from backend.simple_rag_service import SimpleRAGService

        # ----------------------
        # Database initialization
        # ----------------------
        db_service = NeonDBService()
        if await db_service.connect():
            await db_service.create_tables()
            print("✅ Database initialized")
        else:
            print("❌ Database connection failed")
            db_service = None

        app.state.db_service = db_service

        # ----------------------
        # RAG / LLM initialization
        # ----------------------
        rag_service = SimpleRAGService()

        app.state.rag_service = rag_service
        app.state.rag_service_available = rag_service.llm is not None

        print(
            "✅ RAG initialized | LLM available:",
            app.state.rag_service_available
        )

    except Exception as e:
        print("🔥 Startup error:", e)
        app.state.db_service = None
        app.state.rag_service = None
        app.state.rag_service_available = False

    yield  # ---- App is running ----

    # ----------------------
    # Shutdown
    # ----------------------
    if app.state.db_service:
        await app.state.db_service.close()
        print("🛑 Database connection closed")


# -------------------------------------------------------------------
# FastAPI App
# -------------------------------------------------------------------
app = FastAPI(
    title="PAHR RAG Chatbot API",
    version="1.0.0",
    lifespan=lifespan
)

# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-note-book-rkas.vercel.app",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------------------
class QueryRequest(BaseModel):
    question: str


class ChatbotResponse(BaseModel):
    llm_answer: str
    source_documents: List[str]


class SelectedTextRequest(BaseModel):
    selected_text: str
    question: str


class IngestContentRequest(BaseModel):
    chapter_id: str
    content_markdown: str


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "PAHR RAG Chatbot API is running",
        "health": "/api/health",
        "query": "/api/query",
        "ask_selected": "/api/ask-selected",
        "ingest": "/api/ingest-content",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "rag_service_available": app.state.rag_service_available
    }


@app.post("/api/query", response_model=ChatbotResponse)
async def query_chatbot(payload: QueryRequest):
    rag_service = app.state.rag_service

    if not rag_service:
        raise HTTPException(503, "RAG service not available")

    try:
        response = rag_service.query(payload.question)

        # Save chat history (optional, non-fatal)
        db = app.state.db_service
        if db:
            try:
                user_id = 1
                user = await db.get_user(user_id)
                if not user:
                    user_id = await db.add_user(
                        username="default_user",
                        email="default@example.com"
                    )

                if user_id:
                    await db.save_chat_history(
                        user_id=user_id,
                        question=payload.question,
                        answer=response["llm_answer"],
                        source_documents=response["source_documents"],
                    )
            except Exception as db_error:
                print("⚠️ DB error (ignored):", db_error)

        return ChatbotResponse(
            llm_answer=response["llm_answer"],
            source_documents=response["source_documents"],
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, str(e))


@app.post("/api/ask-selected", response_model=ChatbotResponse)
def ask_selected(payload: SelectedTextRequest):
    rag_service = app.state.rag_service

    if not rag_service:
        raise HTTPException(503, "RAG service not available")

    try:
        response = rag_service.ask_selected_text(
            payload.selected_text,
            payload.question
        )

        return ChatbotResponse(
            llm_answer=response["llm_answer"],
            source_documents=response["source_documents"],
        )

    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/ingest-content")
def ingest_content(payload: IngestContentRequest):
    rag_service = app.state.rag_service

    if not rag_service or not rag_service.vector_store_service:
        raise HTTPException(503, "Vector store not available")

    try:
        rag_service.vector_store_service.add_document(
            doc_id=payload.chapter_id,
            content=payload.content_markdown,
            metadata={
                "source": f"chapter_{payload.chapter_id}",
                "type": "markdown",
            },
        )
        return {"message": "Content ingested successfully"}

    except Exception as e:
        raise HTTPException(500, str(e))


# -------------------------------------------------------------------
# Local run only (DO ignores this)
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
