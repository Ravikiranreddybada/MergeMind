#!/bin/bash

# Start Backend in Live Mode
echo "🚀 Starting Backend in LIVE MODE..."

# Set all required environment variables
export GITHUB_TOKEN="your_github_token_here"
export OPENAI_API_KEY="your_openai_api_key_here"

# Verify environment variables are set
echo "✅ Environment Variables:"
echo "   GitHub Token: ${GITHUB_TOKEN:0:10}..."
echo "   OpenAI API Key: ${OPENAI_API_KEY:0:10}..."

# Activate virtual environment and start backend
source venv/bin/activate
echo "🔧 Starting FastAPI backend on http://localhost:8000"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
