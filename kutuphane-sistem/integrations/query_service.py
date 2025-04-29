from typing import Dict, List, Optional
import logging
from .library_api import query_library
from .yordam_token_manager import get_yordam_token, validate_token
from .oai_pmh import query_oai
from .web_scraper import LibraryWebScraper
import openai
import os

logger = logging.getLogger(__name__)

class QueryService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
        self.web_scraper = LibraryWebScraper()

    def process_library_query(self, query: str) -> Optional[str]:
        """Process library catalog query"""
        token = get_yordam_token()
        if not token or not validate_token(token):
            logger.error("YORDAM token alınamadı veya geçersiz")
            return None
            
        library_results = query_library(query, token)
        if not library_results:
            return None
            
        response = "Kütüphane kataloğunda şu kaynakları buldum:<br/><br/>"
        response += "<br/><br/>"
        for i, result in enumerate(library_results, 1):
            response += f"{i}. 📚 {result.get('title', 'Başlık yok')}<br/>"
            if result.get('year'):
                response += f"   🗓️ Yıl: {result['year']}<br/>"
            response += "—" * 30 + "<br/>"
        return response

    def process_academic_query(self, query: str) -> Optional[str]:
        """Process academic resources query"""
        oai_results = query_oai(query)
        if not oai_results:
            return None
            
        response = "Akademik kaynaklarda şu sonuçları buldum:<br/><br/>"
        for i, result in enumerate(oai_results, 1):
            response += f"{i}. 📄 {result['title']}<br/>"
            if result.get('date'):
                response += f"   📅 Tarih: {result['date']}<br/>"
            response += "<br/>"
        return response

    def process_website_query(self, query: str) -> Optional[str]:
        """Process library website related queries"""
        query_lower = query.lower()
        
        if "duyuru" in query_lower or "duyurular" in query_lower:
            return self._get_announcements_response()
        elif "personel" in query_lower or "çalışan" in query_lower:
            return self._get_staff_response()
        elif "iletişim" in query_lower or "adres" in query_lower:
            return self._get_contact_response()
        return None

    def _get_announcements_response(self) -> Optional[str]:
        announcements = self.web_scraper.get_announcements()
        if not announcements:
            return None
            
        response = "Kütüphane duyurularını buldum:<br/><br/>"
        for i, ann in enumerate(announcements, 1):
            response += f"{i}. 📢 {ann['title']}<br/>"
            if ann.get('date'):
                response += f"   📅 Tarih: {ann['date']}<br/>"
            response += "<br/>"
        return response

    def _get_staff_response(self) -> Optional[str]:
        staff = self.web_scraper.get_staff_info()
        if not staff:
            return None
            
        response = "Kütüphane personel bilgileri:<br/><br/>"
        for i, person in enumerate(staff, 1):
            response += f"{i}. 👤 {person['name']}<br/>"
            if person.get('title'):
                response += f"   📋 Görev: {person['title']}<br/>"
            if person.get('email'):
                response += f"   📧 E-posta: {person['email']}<br/>"
            if person.get('phone'):
                response += f"   📞 Telefon: {person['phone']}<br/>"
            response += "<br/>"
        return response

    def _get_contact_response(self) -> Optional[str]:
        contact = self.web_scraper.get_contact_info()
        if not contact:
            return None
            
        response = "Kütüphane iletişim bilgileri:<br/><br/>"
        info_items = []
        if contact.get('address'):
            info_items.append(f"📍 Adres: {contact['address']}")
        if contact.get('phone'):
            info_items.append(f"📞 Telefon: {contact['phone']}")
        if contact.get('email'):
            info_items.append(f"📧 E-posta: {contact['email']}")
        if contact.get('working_hours'):
            info_items.append(f"⏰ Çalışma Saatleri: {contact['working_hours']}")
        
        return "<br/>".join(f"{i}. {item}" for i, item in enumerate(info_items, 1))

    def get_chatgpt_response(self, query: str, is_error: bool = False) -> str:
        """Get response from ChatGPT"""
        try:
            system_content = self._get_system_prompt(is_error)
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": query if not is_error else f"Kullanıcının sorusu: {query}"}
            ]
            
            chat_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500 if not is_error else 300
            )
            
            return self._format_response(chat_response.choices[0].message.content)
        except Exception as e:
            logger.error(f"ChatGPT error: {e}")
            return "Şu anda hizmet veremiyorum. Lütfen daha sonra tekrar deneyin veya kütüphane personeliyle iletişime geçin."

    def _get_system_prompt(self, is_error: bool) -> str:
        """Get appropriate system prompt based on context"""
        if is_error:
            return """
Sen Batman Üniversitesi Kütüphanesi'nde çalışan bir yapay zekâ asistanısın.
Şu anda bir hata durumu var ve kullanıcıya yardımcı olman gerekiyor.
Nazik ve yapıcı bir şekilde:
1. Alternatif öneriler sun
2. Başka nasıl yardımcı olabileceğini belirt
3. Gerekirse kütüphane personeline nasıl ulaşabileceklerini açıkla
"""
        return """
Sen Batman Üniversitesi Kütüphanesi'nde çalışan Türkçe yanıt veren bir yapay zekâ asistanısın. 
Kullanıcı sana herhangi bir konuda soru sorduğunda:

1. Eğer kütüphane ile ilgili genel bir bilgi isteniyorsa, kütüphane hizmetleri, kaynaklar ve çalışma alanları hakkında bilgi ver.
2. Eğer akademik araştırma ile ilgili bir soru ise, araştırma yöntemleri ve kaynak bulma stratejileri öner.
3. Eğer teknik bir sorun bildirildiyse, alternatif çözümler ve iletişim kanalları öner.
4. Her zaman nazik, yardımsever ve profesyonel ol.
5. Cevapların her zaman Türkçe olsun.
6. Bilmediğin bir konu hakkında asla yanlış bilgi verme.
7. Emin olmadığın konularda dürüst ol ve kullanıcıyı doğru kaynaklara yönlendir.
"""

    def _format_response(self, text: str) -> str:
        """Format the response text to use numbered lists when appropriate"""
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            lines = paragraph.split('\n')
            
            if any(line.strip().startswith(('-', '*', '•', '→', '·')) for line in lines):
                numbered_lines = []
                item_count = 1
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith(('-', '*', '•', '→', '·')):
                        content = stripped[1:].strip()
                        numbered_lines.append(f"{item_count}. {content}")
                        item_count += 1
                    else:
                        numbered_lines.append(line)
                formatted_paragraphs.append('<br/>'.join(numbered_lines))
            else:
                sentences = [s.strip() for s in paragraph.split('.') if s.strip()]
                if len(sentences) > 1 and all(len(s) < 100 for s in sentences):
                    numbered_sentences = [f"{i+1}. {s}." for i, s in enumerate(sentences)]
                    formatted_paragraphs.append('<br/>'.join(numbered_sentences))
                else:
                    formatted_paragraphs.append(paragraph)
        
        return '<br/><br/>'.join(formatted_paragraphs) 