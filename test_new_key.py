import os
from dotenv import load_dotenv
from backend.simple_rag_service import SimpleRAGService

# Load environment variables
load_dotenv()

print("Testing direct service call with new API key...")

# Initialize the RAG service
rag_service = SimpleRAGService()

print(f"LLM initialized: {rag_service.llm is not None}")

if rag_service.llm:
    print("Testing a simple query...")
    try:
        response = rag_service.query("What is Python programming?")
        print(f"Response: {response['llm_answer']}")
        print(f"Sources: {response['source_documents']}")
    except Exception as e:
        print(f"Error during query: {e}")
        import traceback
        traceback.print_exc()
else:
    print("LLM was not initialized. Check your API keys and configuration.")