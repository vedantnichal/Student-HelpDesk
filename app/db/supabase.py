from dotenv import load_dotenv
import os
from supabase import Client, create_client

load_dotenv()

SUPABSE_URL=os.getenv('SUPABASE_URL')
SUPABSE_KEY=os.getenv('SUPABASE_KEY')

if not SUPABSE_URL or not SUPABSE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be present in .env"
    )

supabase: Client= create_client(
    SUPABSE_URL,
    SUPABSE_KEY
)


print("hello")