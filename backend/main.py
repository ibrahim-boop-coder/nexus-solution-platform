import re
import smtplib
import dns.resolver
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from duckduckgo_search import DDGS
from typing import List

app = FastAPI(title="Nexus Lead Engine v2.0")

# Update this to your Vercel URL after deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Aggressive Dorks for High-Ticket SaaS
DORKS = {
    "Development": 'site:linkedin.com/in/ ("SaaS Founder" OR "CEO") ("@*.io" OR "@*.ai" OR "@*.tech" OR "@*.co")',
    "Design": 'site:linkedin.com/in/ ("E-commerce Founder" OR "Marketing Agency") "@gmail.com"',
    "Defense": 'site:linkedin.com/in/ ("FinTech Founder" OR "CTO") "@gmail.com"'
}

# Regex targeting high-value TLDs
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:io|ai|co|tech|com)'

class LeadRequest(BaseModel):
    category: str

class LeadResponse(BaseModel):
    name: str
    company: str
    email: str
    is_priority: bool

def verify_email_smtp(email: str) -> bool:
    try:
        domain = email.split('@')[-1]
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
        server = smtplib.SMTP(timeout=7)
        server.connect(mx_record)
        server.helo(server.local_hostname)
        server.mail('verify@nexus-solution.com')
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except:
        return False

@app.post("/api/generate-leads", response_model=List[LeadResponse])
async def generate_leads(request: LeadRequest):
    query = DORKS.get(request.category)
    if not query: raise HTTPException(status_code=400, detail="Invalid Category")

    final_leads = []
    seen = set()

    with DDGS() as ddgs:
        print(f"---> Searching DuckDuckGo for: {query}")
        # Generator ko list mein convert kar rahe hain taake count kar sakein
        results = list(ddgs.text(query, max_results=40))
        
        print(f"---> DuckDuckGo returned {len(results)} results!")
        
        for res in results:
            text = f"{res['title']} {res['body']}".lower()
            emails = re.findall(EMAIL_REGEX, text)
            
            for email in emails:
                if email not in seen_emails:
                    is_high_value = any(email.endswith(tld) for tld in ['.io', '.ai', '.tech'])
                    
                    # SMTP Verification waqti taur par bypass hai
                    if True: 
                        leads.append({
                            "name": res.get('title', '').split('|')[0].strip(),
                            "company": "High-Ticket SaaS" if is_high_value else "Standard Lead",
                            "email": email
                        })
                        seen_emails.add(email)
                        print(f"Found Lead: {email}")