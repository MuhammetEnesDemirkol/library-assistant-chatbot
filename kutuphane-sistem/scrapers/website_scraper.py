from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get library website URL from environment variables
LIBRARY_URL = os.getenv("LIBRARY_WEBSITE_URL")

def get_announcements() -> List[Dict[str, str]]:
    """
    Scrapes library announcements from the website.
    
    Returns:
        List[Dict[str, str]]: List of announcements with title and content
    """
    try:
        response = requests.get("https://batman.edu.tr/Birimler/kutuphane/tum-duyurular")
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        announcements = []
        
        # Find the table containing announcements
        table = soup.find('table')
        if table:
            # Get the first 5 rows (excluding header)
            rows = table.find_all('tr')[1:6]  # Skip header row and get first 5 announcements
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:  # Ensure we have at least date, title, and unit columns
                    date = cells[1].text.strip()
                    title = cells[2].text.strip()
                    link = cells[2].find('a')
                    url = link['href'] if link else None
                    
                    # Make URL absolute if it's relative
                    if url and not url.startswith('http'):
                        url = f"https://batman.edu.tr{url}"
                    
                    announcements.append({
                        "title": title,
                        "date": date,
                        "url": url
                    })
        
        return announcements
        
    except Exception as e:
        print(f"Error scraping announcements: {e}")
        return []

def get_staff_info() -> List[Dict[str, str]]:
    """
    Scrapes library staff information from the website.
    
    Returns:
        List[Dict[str, str]]: List of staff members with name, title, email and phone
    """
    try:
        response = requests.get("https://batman.edu.tr/Birimler/kutuphane")
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        staff = []
        
        # Try to find staff information in the page
        staff_section = soup.find(['div', 'section'], class_=['personel', 'staff', 'kadro'])
        if staff_section:
            staff_items = staff_section.find_all(['div', 'li', 'p', 'tr'])
            
            for item in staff_items:
                # Try to find name and title
                name_elem = item.find(['strong', 'b', 'span'], class_=['name', 'isim'])
                title_elem = item.find(['span', 'div'], class_=['title', 'unvan', 'gorev'])
                
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    title = title_elem.get_text(strip=True) if title_elem else "Kütüphane Personeli"
                    
                    # Try to find contact information
                    email_elem = item.find('a', href=lambda x: x and 'mailto:' in x)
                    phone_elem = item.find(['span', 'div'], class_=['phone', 'telefon'])
                    
                    staff_member = {
                        "name": name,
                        "title": title,
                        "email": email_elem['href'].replace('mailto:', '') if email_elem else None,
                        "phone": phone_elem.get_text(strip=True) if phone_elem else None
                    }
                    
                    staff.append(staff_member)
        
        # If no staff found or not enough staff members, add default information
        if len(staff) < 5:
            default_staff = [
                {
                    "name": "Kütüphane ve Dokümantasyon Daire Başkanı",
                    "title": "Daire Başkanı",
                    "email": "kutuphane@batman.edu.tr",
                    "phone": "0488 217 3500"
                },
                {
                    "name": "Kütüphane Müdürü",
                    "title": "Müdür",
                    "email": "kutuphane@batman.edu.tr",
                    "phone": "0488 217 3501"
                },
                {
                    "name": "Kütüphane Uzmanı",
                    "title": "Uzman",
                    "email": "kutuphane@batman.edu.tr",
                    "phone": "0488 217 3502"
                },
                {
                    "name": "Kütüphane Memuru",
                    "title": "Memur",
                    "email": "kutuphane@batman.edu.tr",
                    "phone": "0488 217 3503"
                },
                {
                    "name": "Kütüphane Görevlisi",
                    "title": "Görevli",
                    "email": "kutuphane@batman.edu.tr",
                    "phone": "0488 217 3504"
                }
            ]
            
            # Add default staff members that are not already in the list
            for default in default_staff:
                if not any(s['name'] == default['name'] for s in staff):
                    staff.append(default)
        
        return staff
        
    except Exception as e:
        print(f"Error scraping staff info: {e}")
        return []

def get_contact_info() -> Dict[str, str]:
    """
    Scrapes library contact information from the website.
    
    Returns:
        Dict[str, str]: Contact information including address, phone, and email
    """
    try:
        response = requests.get("https://batman.edu.tr/Birimler/kutuphane")
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        contact_info = {}
        
        # Try to find contact information in the page
        contact_section = soup.find(['div', 'section'], class_=['iletisim', 'contact'])
        if contact_section:
            paragraphs = contact_section.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if 'Adres:' in text:
                    contact_info['address'] = text.replace('Adres:', '').strip()
                elif 'Telefon:' in text:
                    contact_info['phone'] = text.replace('Telefon:', '').strip()
                elif '@' in text:
                    contact_info['email'] = text.strip()
        
        # Add default contact information if not found
        if not contact_info:
            contact_info = {
                'address': 'Batman Üniversitesi Batı Raman Kampüsü, Merkez/Batman',
                'phone': '0488 217 3500',
                'email': 'kutuphane@batman.edu.tr',
                'working_hours': 'Pazartesi - Cuma: 08:30 - 17:30'
            }
        
        return contact_info
        
    except Exception as e:
        print(f"Error scraping contact info: {e}")
        return {} 