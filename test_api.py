import requests
import json

# Test the API endpoints
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print("Health Check Response:", response.json())
        return response.json()
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return None

def test_query():
    """Test the query endpoint"""
    try:
        payload = {"question": "What is artificial intelligence?"}
        response = requests.post(f"{BASE_URL}/api/query", json=payload)
        print("Query Response:", response.json())
        return response.json()
    except Exception as e:
        print(f"Error testing query endpoint: {e}")
        return None

def test_ask_selected():
    """Test the ask-selected endpoint"""
    try:
        payload = {
            "selected_text": "Artificial intelligence is a branch of computer science that aims to create software or machines that exhibit human-like intelligence.",
            "question": "Can you explain more about AI?"
        }
        response = requests.post(f"{BASE_URL}/api/ask-selected", json=payload)
        print("Ask Selected Response:", response.json())
        return response.json()
    except Exception as e:
        print(f"Error testing ask-selected endpoint: {e}")
        return None

def test_ingest_content():
    """Test the ingest-content endpoint"""
    try:
        payload = {
            "chapter_id": "test_chapter_1",
            "content_markdown": "# Introduction to AI\n\nArtificial intelligence is a branch of computer science..."
        }
        response = requests.post(f"{BASE_URL}/api/ingest-content", json=payload)
        print("Ingest Content Response:", response.json())
        return response.json()
    except Exception as e:
        print(f"Error testing ingest-content endpoint: {e}")
        return None

if __name__ == "__main__":
    print("Testing API endpoints...\n")
    
    print("1. Testing health check...")
    test_health()
    
    print("\n2. Testing query endpoint...")
    test_query()
    
    print("\n3. Testing ask-selected endpoint...")
    test_ask_selected()
    
    print("\n4. Testing ingest-content endpoint...")
    test_ingest_content()
    
    print("\nAll tests completed!")