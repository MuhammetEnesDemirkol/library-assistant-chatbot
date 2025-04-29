from typing import List, Dict
from sickle import Sickle
from sickle.iterator import OAIResponseIterator
import os
from dotenv import load_dotenv
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get OAI-PMH endpoint from environment variables
OAI_ENDPOINT = os.getenv("OAI_PMH_ENDPOINT", "https://earsiv.batman.edu.tr/server/oai/request")

def test_oai_endpoint() -> Dict:
    """
    Tests the OAI-PMH endpoint with various verbs and returns diagnostic information.
    """
    diagnostic_info = {
        "endpoint": OAI_ENDPOINT,
        "identify": None,
        "list_metadata_formats": None,
        "list_identifiers": None,
        "error": None
    }

    try:
        # Test Identify
        params = {'verb': 'Identify'}
        response = requests.get(OAI_ENDPOINT, params=params, timeout=10)
        diagnostic_info["identify"] = {
            "status": response.status_code,
            "content_type": response.headers.get('content-type'),
            "content": response.text[:200] if response.text else None
        }

        # Test ListMetadataFormats
        params = {'verb': 'ListMetadataFormats'}
        response = requests.get(OAI_ENDPOINT, params=params, timeout=10)
        diagnostic_info["list_metadata_formats"] = {
            "status": response.status_code,
            "content_type": response.headers.get('content-type'),
            "content": response.text[:200] if response.text else None,
            "formats": []  # Will be populated if successful
        }

        # If ListMetadataFormats was successful, parse the formats
        if response.status_code == 200:
            try:
                from xml.etree import ElementTree as ET
                root = ET.fromstring(response.text)
                formats = root.findall('.//{http://www.openarchives.org/OAI/2.0/}metadataFormat')
                diagnostic_info["list_metadata_formats"]["formats"] = [
                    format.find('{http://www.openarchives.org/OAI/2.0/}metadataPrefix').text
                    for format in formats
                ]
            except Exception as e:
                logger.error(f"Error parsing metadata formats: {e}")

        # Test ListIdentifiers
        params = {'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc'}
        response = requests.get(OAI_ENDPOINT, params=params, timeout=10)
        diagnostic_info["list_identifiers"] = {
            "status": response.status_code,
            "content_type": response.headers.get('content-type'),
            "content": response.text[:200] if response.text else None
        }

    except Exception as e:
        diagnostic_info["error"] = str(e)
        logger.error(f"OAI-PMH endpoint test hatası: {e}")

    return diagnostic_info

def query_oai(keyword: str) -> List[Dict]:
    """
    Queries the university's OAI-PMH service for records matching the keyword.
    Returns a list of records with title, author, and date information.
    
    Args:
        keyword (str): Search term to find records
        
    Returns:
        List[Dict]: List of records with their details
    """
    try:
        # Test endpoint and get diagnostic info
        diag_info = test_oai_endpoint()
        logger.info("OAI-PMH Diagnostic Info:")
        for verb, info in diag_info.items():
            if verb != "endpoint":
                logger.info(f"{verb}: {info}")

        if diag_info["error"]:
            logger.error("""
            ⚠️ OAI-PMH HATASI:
            DSpace OAI endpoint'e erişilemiyor. Bu durum genellikle şu sebeplerden kaynaklanır:
            1. Endpoint yanlış olabilir
            2. Sunucu yanıt vermiyor olabilir
            3. OAI-PMH servisi kapalı olabilir
            
            Lütfen sistem yöneticisiyle iletişime geçin ve şu bilgileri iletin:
            - Endpoint: https://earsiv.batman.edu.tr/server/oai/
            - Test sonuçları: {diag_info}
            """)
            return []

        # Try different endpoint variations
        endpoints = [
            OAI_ENDPOINT,
            OAI_ENDPOINT.rstrip('/'),
            OAI_ENDPOINT.rstrip('/') + '/request',
            "https://earsiv.batman.edu.tr/oai/request",
            "https://earsiv.batman.edu.tr/oai"
        ]

        sickle = None
        working_endpoint = None

        for endpoint in endpoints:
            try:
                logger.info(f"Trying endpoint: {endpoint}")
                sickle = Sickle(
                    endpoint,
                    headers={'Accept': 'application/xml'},
                    protocol_version="2.0"
                )
                identify = sickle.Identify()
                logger.info(f"Successfully connected to: {endpoint}")
                logger.info(f"Repository name: {identify.repositoryName}")
                working_endpoint = endpoint
                break
            except Exception as e:
                logger.error(f"Failed with endpoint {endpoint}: {str(e)}")
                continue

        if not sickle or not working_endpoint:
            logger.error("Could not connect to any OAI-PMH endpoint")
            return []

        # Get available metadata formats
        try:
            formats = list(sickle.ListMetadataFormats())
            logger.info(f"Available metadata formats: {[f.metadataPrefix for f in formats]}")
        except Exception as e:
            logger.error(f"Error listing metadata formats: {e}")
            formats = []

        # Try to list records
        try:
            records = sickle.ListRecords(metadataPrefix='oai_dc')
        except Exception as e:
            logger.error(f"Error listing records: {e}")
            try:
                # Try listing sets
                sets = list(sickle.ListSets())
                if sets:
                    logger.info(f"Available sets: {[s.setSpec for s in sets]}")
                    records = sickle.ListRecords(
                        metadataPrefix='oai_dc',
                        set=sets[0].setSpec
                    )
                else:
                    logger.error("No sets available")
                    return []
            except Exception as set_error:
                logger.error(f"Error listing sets: {set_error}")
                return []

        results = []
        for record in records:
            try:
                metadata = record.metadata
                if not metadata:
                    continue

                title = metadata.get("title", [""])[0] if "title" in metadata else ""
                creator = metadata.get("creator", [""])[0] if "creator" in metadata else ""
                date = metadata.get("date", [""])[0] if "date" in metadata else ""
                identifier = metadata.get("identifier", [""])[0] if "identifier" in metadata else ""

                if (keyword.lower() in title.lower() or 
                    keyword.lower() in creator.lower()) and title:
                    results.append({
                        "title": title,
                        "creator": creator,
                        "date": date,
                        "identifier": identifier
                    })
                if len(results) >= 5:
                    break

            except Exception as record_error:
                logger.error(f"Error processing record: {record_error}")
                continue

        return results

    except Exception as e:
        logger.error(f"Error querying OAI-PMH service: {e}")
        logger.error("Full error details:", str(e))
        return [] 