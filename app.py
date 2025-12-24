# Hugging Face Spaces entry point
import os
import uvicorn
from main import app

# For Hugging Face Spaces, this serves as the entry point
# The app object is the FastAPI instance that will be served

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)