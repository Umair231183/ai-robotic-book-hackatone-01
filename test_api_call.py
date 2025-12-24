import requests
import json

# Test the API endpoint
def test_api():
    url = "http://localhost:8080/api/query"
    headers = {"Content-Type": "application/json"}
    data = {"question": "Hello, how are you?"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print("API Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api()