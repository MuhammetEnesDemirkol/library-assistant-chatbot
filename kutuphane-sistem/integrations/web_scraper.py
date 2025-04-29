import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
import re
from dotenv import load_dotenv
import os
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LibraryWebScraper:
    def __init__(self):
        self.base_url = os.getenv("LIBRARY_WEBSITE_URL", "https://batman.edu.tr/Birimler/kutuphane")
        self.announcements_url = f"{self.base_url}/tum-duyurular"
        self.staff_url = f"{self.base_url}/idari-kadro"
        self.contact_url = os.getenv("CONTACT_PAGE_URL", f"{self.base_url}/sayfalar/17995")

        logger.info(f"Initialized web scraper with base URL: {self.base_url}")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })

    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            logger.info(f"Fetching URL: {url}")
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            logger.info(f"Successfully fetched URL: {url}")
            return BeautifulSoup(resp.text, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _extract_staff_links(self, soup: BeautifulSoup) -> List[str]:
        links = set()
        for a in soup.find_all('a', href=re.compile(r'pers_id=\d+')):
            href = a['href']
            full = href if href.startswith('http') else urljoin(self.base_url, href)
            links.add(full)
        return list(links)

    def _extract_staff_details(self, soup: BeautifulSoup) -> Dict[str, str]:
        details = {
            'name': '',
            'title': '',
            'unit': '',
            'phone': '',
            'internal_phone': '',
            'email': ''
        }
        form_div = soup.find('div', class_='form')
        if form_div:
            table = form_div.find('table')
            if table:
                for tr in table.find_all('tr'):
                    cols = tr.find_all('td')
                    if len(cols) < 2:
                        continue
                    key = cols[0].get_text(strip=True).rstrip(':')
                    val = cols[1].get_text(strip=True)
                    if key == 'Adı Soyadı':
                        details['name'] = val
                    elif key == 'Ünvanı':
                        details['title'] = val
                    elif key == 'Birimi':
                        details['unit'] = val
                    elif key in ('İş Telefonu', 'Telefon'):
                        details['phone'] = val
                    elif key in ('Dahili Telefon', 'Dahili'):
                        details['internal_phone'] = val
                    elif 'E-posta' in key:
                        a = cols[1].find('a', href=True)
                        if a and 'mailto:' in a['href']:
                            details['email'] = a['href'].replace('mailto:', '').strip()
                        else:
                            details['email'] = val
        if not details['name']:
            labels = soup.find_all('div', class_='pLabel')
            for label in labels:
                text = label.get_text(strip=True).lower()
                value_div = label.find_next_sibling('div', class_='pValue')
                val = value_div.get_text(strip=True) if value_div else ''
                if 'ünvan' in text:
                    details['title'] = val
                elif 'telefon' in text:
                    details['phone'] = val
                elif 'e-posta' in text:
                    details['email'] = val
                elif 'oda no' in text:
                    details['internal_phone'] = val
        return details

    def get_all_staff_details(self) -> List[Dict[str, str]]:
        soup = self._get_soup(self.staff_url)
        if not soup:
            logger.error("Failed to fetch staff listing page")
            return []
        links = self._extract_staff_links(soup)
        logger.info(f"Found {len(links)} unique staff profile links")
        all_details = []
        for link in links:
            profile = self._get_soup(link)
            if not profile:
                continue
            details = self._extract_staff_details(profile)
            if details.get('name'):
                logger.info(f"Processed profile: {details['name']}")
                all_details.append(details)
        logger.info(f"Successfully processed {len(all_details)} staff profiles")
        return all_details

    def get_announcements(self) -> List[Dict[str, str]]:
        soup = self._get_soup(self.announcements_url)
        if not soup:
            return []
        rows = soup.find_all('table')[0].find_all('tr')[1:6]
        announcements = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                title_link = cols[2].find('a')
                title = title_link.get_text(strip=True) if title_link else cols[2].get_text(strip=True)
                url = urljoin(self.base_url, title_link['href']) if title_link else ''
                announcements.append({
                    'title': title,
                    'date': cols[1].get_text(strip=True),
                    'url': url
                })
        return announcements

    def get_contact_info(self) -> Dict[str, Optional[List[str]]]:
        soup = self._get_soup(self.contact_url)
        if not soup:
            return {}
        content = soup.find('div', class_='dinamic-content text-left')
        if not content:
            logger.error("Contact content area not found")
            return {}
        contact = {'address': '', 'phone': [], 'email': ''}
        # Address
        strong = content.find('strong')
        if strong:
            span = strong.find('span')
            contact['address'] = span.get_text(strip=True) if span else strong.get_text(strip=True)
        # Phones
        phones = []
        for img in content.find_all('img', alt=True):
            alt = img['alt'].strip()
            if re.match(r"\+90\s*\d{3}\s*\d{3}\s*\d{4}", alt):
                phones.append(alt)
        contact['phone'] = phones
        # Email
        email_link = content.find('a', href=re.compile(r'mailto:'))
        if email_link:
            contact['email'] = email_link['href'].replace('mailto:', '').strip()
        logger.info(f"Contact information gathering completed: {contact}")
        return contact
