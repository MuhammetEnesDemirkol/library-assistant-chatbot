from typing import List, Dict
import requests
import os
from dotenv import load_dotenv
import logging
from .yordam_token_manager import get_yordam_token, validate_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Configuration
API_URL = "https://katalog.yordamdestek.com/yordam/webservis/webservis.php"

def query_library(query: str, token: str) -> List[Dict]:
    """
    Queries the YORDAM library system for resources.

    Args:
        query (str): Search query
        token (str): Authentication token

    Returns:
        List[Dict]: List of resources found
    """
    if not query or not token:
        logger.error("Query veya token boş olamaz")
        return []

    # Log request details
    logger.info(f"""
    🔍 YORDAM API Sorgu:
    - Endpoint: {API_URL}
    - Arama: {query}
    - Token: {token[:10]}...
    """)

    # Prepare request
    params = {
        "token": token,
        "islem": "arama",
        "q": query,
        "limit": 10,
        "format": "json"
    }

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'BatmanLibrary/1.0',
        'Cache-Control': 'no-cache'
    }

    try:
        # Make request with detailed logging
        response = requests.get(
            API_URL,
            params=params,
            headers=headers,
            timeout=10
        )

        # Log response details
        logger.info(f"""
        📥 YORDAM API Yanıtı:
        - Durum Kodu: {response.status_code}
        - İçerik Tipi: {response.headers.get('content-type')}
        - Yanıt Uzunluğu: {len(response.text) if response.text else 0} bytes
        """)

        # Check response status
        if response.status_code != 200:
            logger.error(f"""
            ❌ YORDAM API Hatası:
            - Durum Kodu: {response.status_code}
            - Yanıt: {response.text}
            """)
            return []

        # Check if response is empty
        if not response.text.strip():
            logger.error("""
            ⚠️ YORDAM API Hatası:
            Sunucudan boş yanıt döndü. Bu durum genellikle şu sebeplerden kaynaklanır:
            1. Token geçersiz olabilir
            2. Sorgu formatı hatalı olabilir
            3. Sunucu yanıt vermiyor olabilir
            """)
            return []

        # Try to parse JSON
        try:
            data = response.json()
            logger.debug(f"Parsed JSON response: {data}")

            if isinstance(data, list):
                logger.info(f"✅ {len(data)} sonuç bulundu")
                return data
            elif isinstance(data, dict):
                if data.get("status") == "error":
                    logger.error(f"API hata döndü: {data.get('message', 'Bilinmeyen hata')}")
                    return []
                elif "response" in data and "docs" in data["response"]:
                    raw_results = data["response"]["docs"]
                    results = []

                    for item in raw_results:
                        results.append({
                            "title": item.get("kunyeEserAdiYazarlar_txt", "Başlık bulunamadı"),
                            "author": "Bilinmiyor",  # YORDAM genelde bu alanı dönmez
                            "year": item.get("qYayinTarihi_str", "Yıl yok")
                        })

                    logger.info(f"✅ {len(results)} düzenlenmiş sonuç döndü")
                    return results
                else:
                    logger.error(f"⚠️ Beklenmeyen yanıt yapısı: {data}")
                    return []

            else:
                logger.error(f"Beklenmeyen yanıt tipi: {type(data)}")
                return []

        except ValueError as e:
            logger.error(f"""
            ❌ JSON parse hatası: {e}
            Ham yanıt: {response.text[:200]}
            """)
            return []

    except requests.exceptions.Timeout:
        logger.error("⏰ Sorgu zaman aşımına uğradı")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Sorgu başarısız: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Beklenmeyen hata: {e}")
        return []

def get_mock_data() -> List[Dict]:
    """
    Returns mock data when the library API is unavailable.
    """
    return [
        {
            "title": "Python Crash Course",
            "author": "Eric Matthes",
            "year": "2019"
        },
        {
            "title": "Learning Python",
            "author": "Mark Lutz",
            "year": "2013"
        },
        {
            "title": "Fluent Python",
            "author": "Luciano Ramalho",
            "year": "2015"
        }
    ]

def query_library_old(keyword: str) -> List[Dict]:
    """
    Searches the library system for books matching the given keyword.
    Currently returns mock data, but can be replaced with real API calls.

    Args:
        keyword (str): Search term to find books

    Returns:
        List[Dict]: List of books with their details
    """
    mock_books = [
        {
            "title": "Python Programming",
            "author": "John Smith",
            "year": 2023,
            "isbn": "978-1234567890",
            "available": True
        },
        {
            "title": "Advanced Python",
            "author": "Jane Doe",
            "year": 2022,
            "isbn": "978-0987654321",
            "available": False
        },
        {
            "title": "Python for Beginners",
            "author": "Mike Johnson",
            "year": 2021,
            "isbn": "978-1122334455",
            "available": True
        }
    ]

    filtered_books = [
        book for book in mock_books
        if keyword.lower() in book["title"].lower() or 
           keyword.lower() in book["author"].lower()
    ]

    return filtered_books
