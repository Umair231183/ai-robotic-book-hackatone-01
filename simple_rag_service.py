from typing import Dict, Any
import os

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage

from langchain_openai import ChatOpenAI

# Optional: Gemini (disabled to avoid quota issues)
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class SimpleRAGService:
    """
    Production-ready RAG service.
    LLM is initialized at runtime (startup), never at import time.
    """

    def __init__(self):
        # --------------------------------------------
        # Load environment variables
        # --------------------------------------------
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        self.llm = None

        # --------------------------------------------
        # Priority 1: Google Gemini (disabled by default)
        # --------------------------------------------
        if GEMINI_AVAILABLE and False:  # Disabled to prevent quota errors
            if self.gemini_api_key:
                try:
                    self.llm = ChatGoogleGenerativeAI(
                        model="gemini-2.0-flash",
                        temperature=0.1,
                        google_api_key=self.gemini_api_key,
                    )
                    self.llm.invoke([HumanMessage(content="ping")])
                    print("✅ Gemini LLM initialized")
                except Exception as e:
                    print("❌ Gemini init failed:", e)
                    self.llm = None

        # --------------------------------------------
        # Priority 2: OpenRouter
        # --------------------------------------------
        if not self.llm and self.openrouter_api_key:
            try:
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.1,
                    openai_api_key=self.openrouter_api_key,
                    openai_api_base="https://openrouter.ai/api/v1"
                )
                self.llm.invoke([HumanMessage(content="ping")])
                print("✅ OpenRouter LLM initialized")
            except Exception as e:
                print("❌ OpenRouter init failed:", e)
                self.llm = None

        # --------------------------------------------
        # Priority 3: OpenAI Direct
        # --------------------------------------------
        if not self.llm and self.openai_api_key:
            try:
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.1,
                    openai_api_key=self.openai_api_key
                )
                self.llm.invoke([HumanMessage(content="ping")])
                print("✅ OpenAI LLM initialized")
            except Exception as e:
                print("❌ OpenAI init failed:", e)
                self.llm = None

        # --------------------------------------------
        # Fallback
        # --------------------------------------------
        if not self.llm:
            print("⚠️ No LLM available — mock responses will be used")

        # Build the QA chain
        self.qa_chain = self._build_chain()

    # --------------------------------------------
    # Build prompt + chain
    # --------------------------------------------
    def _build_chain(self):
        if not self.llm:
            return None

        template = """You are a helpful AI assistant.
Answer clearly and accurately.

Question: {question}
Answer:"""

        prompt = PromptTemplate.from_template(template)

        return (
            {"question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    # --------------------------------------------
    # Query method
    # --------------------------------------------
    def query(self, question: str) -> Dict[str, Any]:
        if not self.llm:
            return {
                "llm_answer": "LLM is not configured properly. Please contact the administrator.",
                "source_documents": [],
            }

        try:
            answer = self.qa_chain.invoke(question) if self.qa_chain else "LLM unavailable"
            return {
                "llm_answer": answer,
                "source_documents": ["General knowledge"],
            }
        except Exception as e:
            print("LLM runtime error:", e)
            return {
                "llm_answer": "An error occurred while generating the response.",
                "source_documents": [],
            }

    # --------------------------------------------
    # Selected text query
    # --------------------------------------------
    def ask_selected_text(self, selected_text: str, question: str) -> Dict[str, Any]:
        combined = f"Context:\n{selected_text}\n\nQuestion:\n{question}"
        return self.query(combined)
