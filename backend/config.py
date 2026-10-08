import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    FLASK_HOST    = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT    = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG   = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.getenv("DATABASE_PATH", "compliance.db")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    AI_MODEL      = os.getenv("AI_MODEL", "gemini-3.1-flash-lite").strip()
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", 1024))