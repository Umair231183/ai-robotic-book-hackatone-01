from simple_rag_service import SimpleRAGService

print("Initializing RAG Service...")
rag_service = SimpleRAGService()

print(f"LLM initialized: {rag_service.llm is not None}")
print(f"LLM object: {rag_service.llm}")

if rag_service.llm:
    print("LLM service is working")
    try:
        response = rag_service.query('Hello, how are you?')
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error during query: {e}")
        import traceback
        traceback.print_exc()
else:
    print("LLM service failed to initialize")
    
print("OpenRouter API key available:", rag_service.openrouter_api_key is not None and rag_service.openrouter_api_key != '')
print("Gemini API key available:", rag_service.gemini_api_key is not None and rag_service.gemini_api_key != '')
print("OpenAI API key available:", rag_service.openai_api_key is not None and rag_service.openai_api_key != 'sk-your-openai-api-key-here')