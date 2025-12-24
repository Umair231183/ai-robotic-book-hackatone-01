# AI Note Book Backend

A FastAPI backend for an AI-powered note-taking application with OpenRouter integration.

## Features

- FastAPI-based REST API
- OpenRouter AI integration (primary)
- Google Gemini support (fallback)
- OpenAI support (fallback)
- Vector database integration with Qdrant
- PostgreSQL database with Neon
- RAG (Retrieval Augmented Generation) capabilities

## Deployment

### Replit

1. Create a new Repl from this repository
2. Add your environment variables in the Secrets/Environment Variables section:
   - `OPENROUTER_API_KEY` - Your OpenRouter API key
   - `NEON_DATABASE_URL` - Your Neon PostgreSQL connection string
   - `QDRANT_URL` - Your Qdrant cloud URL (optional)
   - `QDRANT_API_KEY` - Your Qdrant API key (optional)
   - `COHERE_API_KEY` - Your Cohere API key (optional)
3. Run the application

### Hugging Face Spaces

1. Fork this repository
2. Create a Space with Docker environment (recommended) or Python environment
3. If using Docker environment:
   - The Dockerfile is already provided
   - Add your environment variables in the Space settings:
     - `OPENROUTER_API_KEY` - Your OpenRouter API key
     - `NEON_DATABASE_URL` - Your Neon PostgreSQL connection string
     - Other optional keys as needed
4. If using Python environment:
   - The app.py file serves as the entry point
   - Add your environment variables in the Space settings
5. The application will be served automatically

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenRouter Configuration (for LLM) - Primary LLM (recommended)
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Google Gemini Configuration (for LLM) - Optional, tried first if available
# GEMINI_API_KEY=your-gemini-api-key-here

# OpenAI Configuration (for LLM) - Fallback option
# OPENAI_API_KEY=your-openai-api-key-here

# Cohere Configuration (for embeddings)
# COHERE_API_KEY=your-cohere-api-key-here

# Neon Database Configuration
NEON_DATABASE_URL=your-neon-db-connection-string-here

# Qdrant Configuration (for local development)
# QDRANT_URL=your-qdrant-url-here
# QDRANT_API_KEY=your-qdrant-api-key-here
```

#### Getting API Keys:

1. **OpenRouter (Recommended)**:
   - Go to https://openrouter.ai/
   - Sign up for an account
   - Navigate to Keys page: https://openrouter.ai/keys
   - Create a new key and copy it to `OPENROUTER_API_KEY`

2. **OpenAI**:
   - Go to https://platform.openai.com/
   - Create an account or log in
   - Go to API keys: https://platform.openai.com/api-keys
   - Create a new secret key and copy it to `OPENAI_API_KEY`

3. **Google Gemini**:
   - Go to https://aistudio.google.com/
   - Create an account or log in
   - Get your API key and copy it to `GEMINI_API_KEY`

## API Endpoints

- `GET /` - Root endpoint with API information
- `POST /api/query` - Query the AI with a question
- `POST /api/ask-selected` - Ask about selected text
- `POST /api/ingest-content` - Ingest content into the RAG system
- `GET /api/health` - Health check endpoint

## Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables
6. Run the application: `uvicorn main:app --reload`

## License

MIT