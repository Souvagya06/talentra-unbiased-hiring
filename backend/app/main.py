import json
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import bcrypt
from supabase import create_client, Client
import os
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, Form
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import io
from google import genai

# load env
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# create app FIRST
app = FastAPI()

# THEN configure Gemini


# THEN define routes
# Replace the /analyze route with this:
@app.post("/analyze")
async def analyze_resume(
    file: UploadFile,
    job_description: str = Form(...)
):

    content = await file.read()

    pdf = PdfReader(io.BytesIO(content))
    resume_text = ""

    for page in pdf.pages:
        resume_text += page.extract_text() or ""
    if not resume_text.strip():
        return {
            "score": 0,
            "strengths": [],
            "gaps": ["Could not extract text from PDF"]
        }

    prompt = f"""You are an expert ATS system.
Analyze the resume against the job description.
Return ONLY JSON with no markdown, no preamble:
{{
  "score": <number 0-100>,
  "strengths": ["strength1", "strength2", "strength3"],
  "gaps": ["gap1", "gap2"]
}}

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}"""

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text    

    try:
        cleaned = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(cleaned)
        return parsed
    except Exception as e:
        print("Gemini raw response:", text)
        return {"score": 0, "strengths": [], "gaps": []}


load_dotenv(dotenv_path="../.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/users")
def get_users():
    try:
        response = supabase.table("users").select("*").execute()
        return {"data": response.data}
    except Exception as e:
        return {"error": str(e)}

# ✅ Allow frontend requests (important later for API calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 Path to your frontend pages
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_PATH = os.path.join(BASE_DIR, "../frontend/pages")
app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "../frontend/assets")), name="assets")


# 🏠 Landing Page
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))


@app.get("/index.html")
def serve_index_html():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))


# 📄 Upload Page
@app.get("/upload.html")
def serve_upload():
    return FileResponse(os.path.join(FRONTEND_PATH, "upload.html"))


# 🎙️ Interview Page
@app.get("/interview.html")
def serve_interview():
    return FileResponse(os.path.join(FRONTEND_PATH, "interview.html"))


# 📊 Result Page
@app.get("/result.html")
def serve_result():
    return FileResponse(os.path.join(FRONTEND_PATH, "result.html"))


# 📄 Report Page
@app.get("/report.html")
def serve_report():
    return FileResponse(os.path.join(FRONTEND_PATH, "report.html"))


# About Page
@app.get("/about.html")
def serve_about():
    return FileResponse(os.path.join(FRONTEND_PATH, "about.html"))


# Contact Page
@app.get("/contact.html")
def serve_contact():
    return FileResponse(os.path.join(FRONTEND_PATH, "contact.html"))


# Legal Page
@app.get("/legal.html")
def serve_legal():
    return FileResponse(os.path.join(FRONTEND_PATH, "legal.html"))


# Login Page
@app.get("/login.html")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_PATH, "login.html"))


@app.post("/signup")
async def signup(request: Request):
    data = await request.json()

    email = data.get("email")

    # check if user already exists
    existing = supabase.table("users").select("*").eq("email", email).execute()

    if existing.data:
        return {"message": "User already exists"}

    # insert new user
    hashed_password = bcrypt.hashpw(
        data.get("password").encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    supabase.table("users").insert({
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "password": hashed_password,
        "role": "user"
    }).execute()

    return {"message": "New User Created"}


@app.post("/login")
async def login(request: Request):
    data = await request.json()

    email = data.get("email")
    password = data.get("password")

    user = supabase.table("users").select("*").eq("email", email).execute()

    if not user.data:
        return {"message": "User doesn't exist"}

    stored_password = user.data[0]["password"]

    # compare hashed password
    if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        return {"message": "Invalid credentials"}

    return {"message": "Login successful"}
