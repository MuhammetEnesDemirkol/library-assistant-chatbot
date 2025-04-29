from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
from dotenv import load_dotenv
from integrations.query_service import QueryService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Batman Üniversitesi Kütüphane Asistanı",
    description="Kütüphane kaynaklarını arama ve bilgi alma sistemi",
    version="1.0.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
query_service = QueryService()

class Query(BaseModel):
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Yapay zeka konusunda kitap arıyorum"
            }
        }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Ana sayfa"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/sorgula")
async def sorgula(query: Query):
    """
    Kullanıcı sorgusunu işle ve yanıt döndür.
    Sırasıyla:
    1. Kütüphane kataloğunu kontrol et
    2. Akademik kaynakları kontrol et
    3. Website bilgilerini kontrol et
    4. Son çare olarak ChatGPT'yi kullan
    """
    try:
        # Step 1: Library catalog
        library_response = query_service.process_library_query(query.query)
        if library_response:
            return {"response": library_response}

        # Step 2: Academic resources
        academic_response = query_service.process_academic_query(query.query)
        if academic_response:
            return {"response": academic_response}

        # Step 3: Website information
        website_response = query_service.process_website_query(query.query)
        if website_response:
            return {"response": website_response}

        # Step 4: ChatGPT fallback
        return {"response": query_service.get_chatgpt_response(query.query)}

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {"response": query_service.get_chatgpt_response(query.query, is_error=True)}

@app.get("/bilgiler", response_class=HTMLResponse)
async def bilgiler(request: Request):
    """Kütüphane bilgilerini görüntüle"""
    try:
        # Get announcements
        announcements = query_service.web_scraper.get_announcements()
        
        # Get staff info
        staff = query_service.web_scraper.get_all_staff_details()
        
        # Get contact info
        contact = query_service.web_scraper.get_contact_info()

        return templates.TemplateResponse(
            "bilgiler.html",
            {
                "request": request,
                "announcements": announcements,
                "staff": staff,
                "contact": contact
            }
        )
    except Exception as e:
        logger.error(f"Error getting library information: {e}")
        return templates.TemplateResponse(
            "bilgiler.html",
            {
                "request": request,
                "error": "Bilgiler alınırken bir hata oluştu. Lütfen daha sonra tekrar deneyin."
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 