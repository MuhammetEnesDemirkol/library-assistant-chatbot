import os
import requests
from dotenv import load_dotenv
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Configuration
API_URL = os.getenv("LIBRARY_API_URL", "").strip()
API_USER = os.getenv("YORDAM_USERNAME", "").strip()
API_PASS = os.getenv("YORDAM_PASSWORD", "").strip()

# Token cache
TOKEN_CACHE = {
    "token": None,
    "expiry": None
}

def get_diagnostic_info() -> Dict:
    """
    Returns diagnostic information about the API connection.
    """
    return {
        "endpoint": API_URL,
        "user": API_USER,
        "has_password": bool(API_PASS),
        "test_url": f"{API_URL}?islem=token&kullanici={API_USER}&sifre=***"
    }

def get_yordam_token() -> Optional[str]:
    """
    Returns manually set static token from .env file.
    """
    token = os.getenv("STATIC_YORDAM_TOKEN", "").strip()
    if token:
        logger.info("📦 Statik token .env dosyasından alındı.")
        return token
    else:
        logger.error("❌ STATIC_YORDAM_TOKEN .env dosyasında bulunamadı.")
        return None

def validate_token(token: str) -> bool:
    """
    Token doğrulaması devre dışı bırakıldı.
    """
    return True 