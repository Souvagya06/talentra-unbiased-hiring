import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    response = supabase.table("users").select("*").execute()
    for user in response.data:
        print(f"'{user.get('first_name')}' '{user.get('last_name')}'")
except Exception as e:
    print(f"Error: {e}")
