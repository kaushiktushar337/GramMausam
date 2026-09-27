import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "GramMausam AI Backend")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DATABASE_URL = os.getenv("DATABASE_URL", "")
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
MODEL_DIR = BASE_DIR / os.getenv("MODEL_DIR", "models")

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
CORS_ORIGINS = [item.strip() for item in origins.split(",") if item.strip()]
