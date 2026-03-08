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
        results = ddgs.text(query, max_results=40)
        for res in results:
            content = f"{res['title']} {res['body']}".lower()
            found_emails = re.findall(EMAIL_REGEX, content)
            
            for email in found_emails:
                if email not in seen:
                    if verify_email_smtp(email):
                        # Logic: If domain is tech-heavy, mark as Priority
                        is_pri = any(email.endswith(t) for t in ['.io', '.ai', '.tech'])
                        
                        # Clean up Name/Company from snippet
                        parts = res['title'].split('|')[0].split('-')
                        name = parts[0].strip() if len(parts) > 0 else "Tech Lead"
                        comp = parts[1].strip() if len(parts) > 1 else "SaaS Startup"
                        
                        final_leads.append({
                            "name": name,
                            "company": comp,
                            "email": email,
                            "is_priority": is_pri
                        })
                        seen.add(email)
    return final_leads

# requirements.txt: fastapi, uvicorn, duckduckgo-search, dnspython, pydantic