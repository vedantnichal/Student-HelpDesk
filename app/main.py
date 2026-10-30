from fastapi import FastAPI, HTTPException
import json

from app.services.gmail_service import get_recent_emails, get_gmail_service, get_email_body
from app.services.llm.base import analyze_mail
from app.schemas import mail_eval
from app.db.supabase import supabase

app= FastAPI()

#helper funct to insert the data in db
def insert_email_data(id: str, analysis: mail_eval):
    try:
        supabase.table("emails").insert({
            "email_id": id,
            "analysis": analysis.model_dump(mode="json")
        }).execute()

    except Exception as e:
        print("Error saving to database:", e)

#helper for bool if the email_id is already in the db
def check_existing_email(id: str):
    data= supabase.table("emails").select("email_id").eq("email_id", id).execute()
    return len(data.data) > 0

# print(check_existing_email("1a18ce72bb5d8c1f"))

# anal="""
#     {
#       "category": "announcement",
#       "course": null,
#       "title": "Promotional recap of features inside the Federal Bank app",
#       "summary": "The email offers a short recap of features available inside the Federal Bank mobile app, includes promotional content, a disclaimer, and an unsubscribe option.",
#       "action_required": false,
#       "deadline": null,
#       "event_date": null,
#       "location": null,
#       "confidence_score": 0.96,
#       "priority": "low"
#     }
# """

# insert_email_data("1a18ce72bb5d8c1f", anal)


#_________________________________
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

@app.get("/emails/{email_id}/analysis")
def analyze_email(email_id: str):
    try:
        service= get_gmail_service()

        mail= (
            service.users()
            .messages()
            .get(userId="me", id=email_id, format="full")
            .execute()
        )

        headers= mail.get("payload", {}).get("headers", [])
        header_data= {
            header["name"].lower():header["value"]
            for header in headers
        }

        body= get_email_body(mail.get("payload", {}))

        email_text= (
            f"subject: {header_data.get('subject', '(No subject)')}\n"
            f"from: {header_data.get('from', 'Unknown sender')}\n"
            f"Date: {header_data.get('date', 'Unknown date')}\n"
            f"{body or mail.get('snippet', '')}"
        )

        # return {
        #     "data": email_text
        # }

        analysis= analyze_mail(email_text)
        # return {
        #     "analysis": analysis
        # }
        return {
            "email_id": email_id,
            "subject": header_data.get('subject', '(No Subject)'),
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(
            status_code= 502,
            detail= "Failed to analyze email"
        )

@app.get("/emails/analyze_bunch/{limit}")
def analyze_email_bunch(limit:int = 10):
    if(limit<1 or limit>50):
        raise HTTPException(
            status_code= 400,
            detail= "Limit must be btn 1 and 50"
        )
    try:
        emails= get_recent_emails(limit)

        # analysis= analyze_mail(emails[0])
        # return{
        #     'analysis': analysis
        # }

        complete_analysis=[]
        for email_data in emails:
            id= email_data["id"]

            if check_existing_email(id):
                analysis= supabase.table("emails").select("analysis").eq("email_id", id).execute()
                complete_analysis.append(analysis.data[0]['analysis'])
                print("ready-made")
            else:
                analysis= analyze_mail(str(email_data))
                complete_analysis.append(analysis)
                insert_email_data(id, analysis)
                print("done")
        return{
            "count": limit,
            "emails_analysis": complete_analysis
        }
    except Exception as e:
        raise HTTPException(
            status_code= 502,
            detail= "Failed to analyze emails"
        )


# print(analyze_email_bunch(2))