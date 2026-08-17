# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Gemini / Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your_google_api_key_here")
GEMINI_MODEL = "models/gemini-2.5-flash"

# File paths
SOP_FILE_PATH = "ACE5_SOP.docx"
CACHE_FILE = "sop_cache.pkl"

# App settings
MAX_DOCUMENT_LENGTH = 30000
CACHE_ENABLED = True

# Flask
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000
