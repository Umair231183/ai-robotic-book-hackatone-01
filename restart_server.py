import os
import sys
import subprocess

print("Stopping any existing server processes...")
print("Please manually stop the existing server (Ctrl+C in the server terminal) if it's running")
print("Then run: python -c \"import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8080)\"")

# Start the server with fresh environment
if __name__ == "__main__":
    import uvicorn
    import main
    print("Starting server with fresh configuration...")
    uvicorn.run(main.app, host="0.0.0.0", port=8080)