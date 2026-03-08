from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from googlesearch import search
import time

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
    print(f"Engine Starting ---> Searching Google for: {query}")
    
    try:
        # DuckDuckGo ki jagah ab Google use ho raha hai
        results = search(query, num_results=20, advanced=True)
        
        for res in results:
            text = f"{res.title} {res.description}".lower()
            emails = re.findall(EMAIL_REGEX, text)
            
            for email in emails:
                if email not in seen_emails:
                    is_premium = any(email.endswith(tld) for tld in ['.io', '.ai', '.tech', '.org'])
                    
                    leads.append({
                        "name": res.title.split('|')[0].split('-')[0].strip()[:20],
                        "company": "🔥 Premium Target" if is_premium else "Standard Target",
                        "email": email
                    })
                    seen_emails.add(email)
                    print(f"Success ---> Found Lead: {email}")
            
            # Google ko block karne se rokne ke liye chota sa pause
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Scraping Error: {e}")
        
    return leads