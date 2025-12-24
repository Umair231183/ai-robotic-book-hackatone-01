import os
from dotenv import load_dotenv
from simple_rag_service import SimpleRAGService



# Load environment variables
load_dotenv()

print("Testing OpenRouter configuration...")

# Initialize the RAG service
rag_service = SimpleRAGService()

print(f"LLM initialized: {rag_service.llm is not None}")
print(f"OpenRouter API key available: {os.getenv('OPENROUTER_API_KEY') is not None and os.getenv('OPENROUTER_API_KEY') != ''}")

if rag_service.llm:
    print("Testing a simple query...")
    try:
        response = rag_service.query("Hello, how are you?")
        print(f"Response: {response['llm_answer']}")
    except Exception as e:
        print(f"Error during query: {e}")
else:
    print("LLM was not initialized. Check your API keys and configuration.")