from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LeadRequest(BaseModel):
    category: str

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

@app.post("/api/generate-leads")
async def generate_leads(req: LeadRequest):
    leads = []
    seen_emails = set()
    
    # Specific targeted query for high-quality leads
    query = f'"{req.category}" "email" (site:linkedin.com OR site:github.com OR site:twitter.com)'
    encoded_query = urllib.parse.quote_plus(query)
    
    print(f"Engine Starting ---> Searching BING for: {query}")
    
    # Fake browser bhej rahe hain taake Bing block na kare
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Bing ke pehle 2 pages (20 results) scrape karenge
        for first in [1, 11]:
            url = f"https://www.bing.com/search?q={encoded_query}&first={first}"
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = soup.find_all('li', class_='b_algo')
            
            for res in results:
                text = res.get_text().lower()
                emails = re.findall(EMAIL_REGEX, text)
                
                title_elem = res.find('h2')
                title = title_elem.get_text()[:25] if title_elem else "Verified Lead"
                
                for email in emails:
                    if email not in seen_emails:
                        is_premium = any(email.endswith(tld) for tld in ['.io', '.ai', '.tech', '.org'])
                        
                        leads.append({
                            "name": title.split('|')[0].split('-')[0].strip(),
                            "company": "🔥 Premium Target" if is_premium else "Standard Target",
                            "email": email
                        })
                        seen_emails.add(email)
                        print(f"Success ---> Found Lead: {email}")
            
            # Thora sa wait taake IP block na ho
            time.sleep(1)
            
    except Exception as e:
        print(f"Scraping Error: {e}")
        
    return leads