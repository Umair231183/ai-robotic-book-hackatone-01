# rag_service.py

from typing import List, Dict, Any
import os
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_qdrant import Qdrant

from .vector_store_service import VectorStoreService

# Load environment variables
load_dotenv()

# --- OpenRouter wrapper ---
try:
    from langchain_openai import ChatOpenAI as OpenAIChat
    OPENROUTER_AVAILABLE = True

    class ChatOpenRouter:
        """Wrapper for using OpenRouter API as LangChain-compatible Chat LLM."""
        def __init__(self, model="openai/gpt-3.5-turbo", temperature=0.1, openrouter_api_key=None):
            if not openrouter_api_key:
                raise ValueError("OpenRouter API key is required.")

            self._llm = OpenAIChat(
                model=model,
                temperature=temperature,
                api_key=openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )

        def invoke(self, input_data):
            return self._llm.invoke(input_data)

        def __call__(self, input_data):
            return self._llm.invoke(input_data)

except ImportError:
    OPENROUTER_AVAILABLE = False
    ChatOpenRouter = None
    print("Warning: OpenRouter not available, fallback to OpenAI.")


# --- RAG Service ---
class RAGService:
    """Retrieval-Augmented Generation service using OpenRouter/OpenAI + Qdrant."""

    def __init__(self):
        # --- API keys ---
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.cohere_api_key = os.getenv("COHERE_API_KEY")

        # --- Initialize Vector Store ---
        try:
            self.vector_store_service = VectorStoreService()
            self.qdrant_client = self.vector_store_service.client
            self.collection_name = self.vector_store_service.collection_name
        except Exception as e:
            print(f"Warning: Could not initialize vector store: {e}")
            self.vector_store_service = None
            self.qdrant_client = None
            self.collection_name = None

        # --- Initialize embeddings ---
        self.embeddings = None
        try:
            if self.cohere_api_key and self.cohere_api_key != "your-cohere-api-key-here":
                self.embeddings = CohereEmbeddings(cohere_api_key=self.cohere_api_key, model="embed-english-v3.0")
                print("Using Cohere embeddings")
                if self.vector_store_service:
                    self.vector_store_service.update_embedding_dimensions(1024)
            elif self.openai_api_key and self.openai_api_key != "sk-your-openai-api-key-here":
                self.embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
                print("Using OpenAI embeddings")
                if self.vector_store_service:
                    self.vector_store_service.update_embedding_dimensions(1536)
            else:
                print("No valid embeddings API key found.")
        except Exception as e:
            print(f"Error initializing embeddings: {e}")

        # --- Initialize LLM ---
        self.llm = None
        try:
            if self.openrouter_api_key and OPENROUTER_AVAILABLE:
                self.llm = ChatOpenRouter(
                    model="openai/gpt-3.5-turbo",
                    temperature=0.1,
                    openrouter_api_key=self.openrouter_api_key
                )
                print("Using OpenRouter LLM")
            elif self.openai_api_key:
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.1,
                    api_key=self.openai_api_key
                )
                print("Using OpenAI LLM")
            else:
                print("No LLM API key found. Service will return mock responses.")
        except Exception as e:
            print(f"Error initializing LLM: {e}")

        # --- Initialize Qdrant retriever ---
        self.retriever = None
        if self.qdrant_client and self.embeddings:
            try:
                from langchain_qdrant import QdrantVectorStore
                self.qdrant_vectorstore = QdrantVectorStore(
                    client=self.qdrant_client,
                    collection_name=self.collection_name,
                    embeddings=self.embeddings
                )
                self.retriever = self.qdrant_vectorstore.as_retriever(search_kwargs={"k": 5})
                print("QdrantVectorStore retriever initialized")
            except Exception as e:
                print(f"Warning: QdrantVectorStore retriever not available: {e}")
                # Fallback to original Qdrant class if QdrantVectorStore fails
                try:
                    self.qdrant_vectorstore = Qdrant(
                        client=self.qdrant_client,
                        collection_name=self.collection_name,
                        embeddings=self.embeddings
                    )
                    self.retriever = self.qdrant_vectorstore.as_retriever(search_kwargs={"k": 5})
                    print("Legacy Qdrant retriever initialized")
                except Exception as fallback_e:
                    print(f"Both Qdrant initializations failed: {e}, {fallback_e}")
                    self.retriever = None

        # --- Build QA chain ---
        self.qa_chain = self._build_qa_chain()

    def _build_qa_chain(self):
        if not self.llm:
            return None

        # If retriever exists, build retrieval-based chain
        if self.retriever:
            template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
            prompt = PromptTemplate.from_template(template)

            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            return (
                {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
        else:
            # Fallback: simple LLM without context
            template = """You are an AI assistant. Answer the user's question using general knowledge.

Question: {question}

Answer:"""
            prompt = PromptTemplate.from_template(template)
            return ({"question": RunnablePassthrough()} | prompt | self.llm | StrOutputParser())

    # --- Query methods ---
    def query(self, question: str) -> Dict[str, Any]:
        if not self.qa_chain:
            return {
                "llm_answer": f"Cannot answer: No LLM configured. Question: {question}",
                "source_documents": []
            }

        try:
            answer = self.qa_chain.invoke(question)
            # Retrieve source docs if retriever exists
            if self.retriever:
                try:
                    source_docs = self.retriever.invoke(question)
                    sources = [doc.metadata.get("source", "Unknown") for doc in source_docs]
                except Exception:
                    sources = ["Content retrieval not available"]
            else:
                sources = ["No retriever configured"]

            return {"llm_answer": answer, "source_documents": sources}
        except Exception as e:
            return {"llm_answer": f"Error: {str(e)}", "source_documents": []}

    def ask_selected_text(self, selected_text: str, question: str) -> Dict[str, Any]:
        enhanced_question = f"Based on the following text: '{selected_text}', {question}"
        return self.query(enhanced_question)

    def safety_check(self, response: str) -> bool:
        lower_response = response.lower()
        harmful_keywords = ["harmful", "offensive", "inappropriate", "malicious", "dangerous", "threatening", "violence", "hate"]
        return not any(kw in lower_response for kw in harmful_keywords)
