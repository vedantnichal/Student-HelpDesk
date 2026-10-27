import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Allow the application to read Gmail messages.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")


def get_gmail_service():
    """Authenticate with Google and return a Gmail API service."""

    creds = None

    # Reuse previously saved authorization if available.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    # Refresh an expired token or start the OAuth flow.
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "credentials.json was not found in the project root."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )

            creds = flow.run_local_server(port=0)

        # Save the token for subsequent runs.
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

        # Restrict access to the token file on Unix-like systems.
        os.chmod(TOKEN_FILE, 0o600)

    # Build and return the Gmail API client.
    service = build(
        "gmail",
        "v1",
        credentials=creds,
    )

    return service


def get_recent_emails(limit=10):
    """Return basic information about the most recent Gmail messages."""

    service = get_gmail_service()

    # Get the IDs of recent messages.
    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=limit,
        )
        .execute()
    )

    messages = response.get("messages", [])
    emails = []

    # Fetch metadata for each message.
    for message in messages:
        email = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message["id"],
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )

        headers = email.get("payload", {}).get("headers", [])

        # Convert headers into a convenient dictionary.
        header_data = {
            header["name"].lower(): header["value"]
            for header in headers
        }

        emails.append(
            {
                "id": email["id"],
                "subject": header_data.get(
                    "subject", "(No subject)"
                ),
                "sender": header_data.get(
                    "from", "Unknown sender"
                ),
                "date": header_data.get(
                    "date", "Unknown date"
                ),
                "snippet": email.get("snippet", ""),
            }
        )

    return emails


if __name__ == "__main__":
    try:
        emails = get_recent_emails(limit=10)

        print(f"\nRetrieved {len(emails)} emails.\n")

        for index, email in enumerate(emails, start=1):
            print(f"Email {index}")
            print(f"Subject: {email['subject']}")
            print(f"From:    {email['sender']}")
            print(f"Date:    {email['date']}")
            print(f"Snippet: {email['snippet']}")
            print("-" * 60)

    except Exception as error:
        print(f"Gmail connection failed: {error}")