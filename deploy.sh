#!/bin/bash
# Deployment script for AI Note Book Backend

echo "Starting deployment for AI Note Book Backend..."

# Check if we're in a Replit environment
if [ -n "$REPL_SLUG" ]; then
    echo "Detected Replit environment"
    echo "Starting application with uvicorn..."
    uvicorn main:app --host 0.0.0.0 --port $PORT
elif [ -n "$SPACE_APP_NAME" ]; then
    # Hugging Face Spaces environment
    echo "Detected Hugging Face Spaces environment"
    echo "Starting application with uvicorn..."
    uvicorn main:app --host 0.0.0.0 --port $PORT
else
    # Regular deployment
    echo "Starting application with uvicorn on default port 8080..."
    uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
fi