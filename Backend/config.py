"""
Backend Configuration
Contains environment-specific settings and constants
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server Configuration
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 7860))  # HF Spaces uses 7860

# API Configuration
BASE_URL = os.getenv("BASE_URL", f"http://localhost:{PORT}")
API_VERSION = "v1"

# CORS Configuration - Add your deployed frontend URL here
ALLOWED_ORIGINS = [
    "http://localhost:4200",  # Angular dev server
    "http://localhost:3000",  # Alternative frontend port
    "*",  # Allow all origins for HF Spaces (update with specific frontend URL in production)
]

# External Services
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
