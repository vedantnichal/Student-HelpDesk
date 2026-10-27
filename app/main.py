from fastapi import FastAPI, HTTPException

from app.services.gmail_service import get_recent_emails

app= FastAPI()

@app.get("/")
def home():
    return {'message': 'Hello, this is home page'}

@app.get("/emails")
def get_emails(limit: int= 10):
    if(limit<1 or limit>50):
        raise HTTPException(
            status_code= 400,
            detail= "Limit must be btn 1 and 50"
        )
    try:
        emails= get_recent_emails(limit= limit)
        return {
            "count": len(emails),
            "emails": emails
        }
    except Exception:
        raise HTTPException(
            status_code= 500,
            detail= "Failed to fetch emails"
        )