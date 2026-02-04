"""
Backend Configuration
Contains environment-specific settings and constants
"""
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "http://localhost:8000"
API_VERSION = "v1"

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:4200",  # Angular dev server
    "http://localhost:3000",  # Alternative frontend port
]

# RapidAPI Configuration (for news service)
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
RAPIDAPI_URL = os.getenv("RAPIDAPI_URL")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
# Server Configuration
HOST = "0.0.0.0"
PORT = 8000
