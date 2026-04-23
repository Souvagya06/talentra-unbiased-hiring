import json
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Request
import bcrypt
from supabase import create_client, Client
import os
from fastapi import FastAPI, UploadFile, Form
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import io
from google import genai
from groq import Groq
import asyncio
import uuid
from pydantic import BaseModel

class UsernameCheck(BaseModel):
    username: str

# load env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing Supabase credentials")

# create app FIRST
app = FastAPI()

# Load Groq client once
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=300.0)

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
Return ONLY valid JSON with no markdown, no preamble:
{{
  "score": <number 0-100 indicating match percentage>,
  "strengths": ["strength1", "strength2", "strength3"],
  "gaps": ["gap1", "gap2"],
  "name": "Extract full name from resume. Return empty string if not found.",
  "email": "Extract email from resume. Return empty string if not found.",
  "phone": "Extract phone from resume. Return empty string if not found.",
  "github_url": "Extract github url from resume. Return empty string if not found.",
  "linkedin_url": "Extract linkedin url from resume. Return empty string if not found."
}}

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}"""

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    models_to_try = ["gemini-2.5-flash-lite"]
    response = None

    for model_name in models_to_try:
        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=model_name,
                contents=prompt
            )
            break
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue

    if not response:
        return {"technical_score": 0, "communication_score": 0, "feedback": "AI service unavailable, please try again."}

    text = response.text

    try:
        cleaned = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(cleaned)
        return parsed
    except Exception as e:
        print("Gemini raw response:", text)
        return {"score": 0, "strengths": [], "gaps": []}


@app.post("/analyze-interview")
async def analyze_interview(
    file: UploadFile,
    user_email: str = Form("test@gmail.com"),
    name: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    github_url: str = Form(""),
    linkedin_url: str = Form(""),
    job_description: str = Form(""),
    resume_score: str = Form("0")
):
    # ✅ moviepy imported lazily here to avoid startup crash
    import moviepy.editor as mp

    content = await file.read()
    filename = file.filename.lower()

    unique_id = uuid.uuid4().hex
    ext = ".wav" if filename.endswith(".wav") else ".webm"
    temp_input = f"temp_input_{unique_id}{ext}"

    with open(temp_input, "wb") as f:
        f.write(content)

    temp_audio = temp_input

    if filename.endswith((".mp4", ".webm", ".mov", ".mkv")):
        try:
            temp_extracted = f"temp_audio_{unique_id}.wav"
            video = mp.VideoFileClip(temp_input)
            if video.audio is not None:
                video.audio.write_audiofile(temp_extracted, logger=None)
                temp_audio = temp_extracted
            video.close()
        except Exception as e:
            pass

    try:
        r_score = int(float(resume_score))
    except:
        r_score = 0

    with open(temp_audio, "rb") as audio_file:
        audio_data = audio_file.read()

    if len(audio_data) > 25 * 1024 * 1024:
        return {"error": "File too large. Please limit recording to under 25MB."}

    transcription = groq_client.audio.transcriptions.create(
        file=(os.path.basename(temp_audio), audio_data),
        model="whisper-large-v3"
    )

    transcript = transcription.text

    if not transcript:
        return {"analysis": "No speech detected"}

    name_instruction = f"The candidate's name is '{name}'. Please use their name in the summary instead of making one up. Make sure the name spelling is exactly as provided." if name else "Do not assume a candidate name if not explicitly mentioned in the transcript."

    prompt = f"""
    You are an interview evaluator.
    {name_instruction}

    Analyze this transcript and return ONLY valid JSON:

    {{
        "technical_score": <number 0-100>,
        "communication_score": <number 0-100>,
        "strengths": ["point1", "point2"],
        "gaps": ["gap1", "gap2"],
        "evaluation_summary": "A short 2-3 sentence paragraph summarizing candidate performance.",
        "recommendation_percentage": <number 0-100, based on overall fit>,
        "recommendation": "Strong Hire" or "Consider" or "Not Recommended"
    }}

    Transcript:
    {transcript}
    """

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    models_to_try = ["gemini-2.5-flash-lite"]
    response = None

    for model_name in models_to_try:
        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=model_name,
                contents=prompt
            )
            break
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue

    if not response:
        return {"technical_score": 0, "communication_score": 0, "feedback": "AI service unavailable, please try again."}

    text = response.text

    try:
        cleaned = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(cleaned)

        insert_response = supabase.table("reports").insert({
            "user_email": user_email,
            "name": name,
            "email": email,
            "phone": phone,
            "github_url": github_url,
            "linkedin_url": linkedin_url,
            "job_description": job_description,
            "resume_score": r_score,
            "technical_score": parsed.get("technical_score", 0),
            "communication_score": parsed.get("communication_score", 0),
            "strengths": parsed.get("strengths", []),
            "gaps": parsed.get("gaps", []),
            "evaluation_summary": parsed.get("evaluation_summary", ""),
            "recommendation_percentage": parsed.get("recommendation_percentage", 0)
        }).execute()

        if insert_response.data and len(insert_response.data) > 0:
            parsed["report_id"] = insert_response.data[0].get("id")

        return parsed

    except Exception as e:
        print("Error saving to supabase:", e)
        return {
            "analysis": text,
            "transcript": transcript[:500]
        }


@app.post("/check-username")
async def check_username(data: UsernameCheck):
    try:
        username = data.username.strip().lower()

        parts = username.split()
        if len(parts) < 2:
            return {"exists": False}

        first_name = parts[0]
        last_name = parts[-1]

        response = supabase.table("users").select("*").execute()

        if not response.data:
            return {"exists": False}

        for user in response.data:
            db_first = (user.get("first_name") or "").strip().lower()
            db_last = (user.get("last_name") or "").strip().lower()

            if db_first == first_name and db_last == last_name:
                return {"exists": True}

        return {"exists": False}

    except Exception as e:
        print("ERROR:", e)
        return {"exists": False}


@app.get("/my-reports")
def get_reports(email: str):
    res = supabase.table("reports") \
        .select("*") \
        .eq("user_email", email) \
        .order("created_at", desc=True) \
        .execute()
    return res.data


@app.get("/report/{id}")
def get_single_report(id: str):
    res = supabase.table("reports") \
        .select("*") \
        .eq("id", id) \
        .single() \
        .execute()
    return res.data


@app.get("/users")
def get_users():
    try:
        response = supabase.table("users").select("*").execute()
        return {"data": response.data}
    except Exception as e:
        return {"error": str(e)}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_PATH = os.path.join(BASE_DIR, "../frontend/pages")
app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "../frontend/assets")), name="assets")


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))

@app.get("/index.html")
def serve_index_html():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))

@app.get("/upload.html")
def serve_upload():
    return FileResponse(os.path.join(FRONTEND_PATH, "upload.html"))

@app.get("/interview.html")
def serve_interview():
    return FileResponse(os.path.join(FRONTEND_PATH, "interview.html"))

@app.get("/result.html")
def serve_result():
    return FileResponse(os.path.join(FRONTEND_PATH, "result.html"))

@app.get("/report.html")
def serve_report():
    return FileResponse(os.path.join(FRONTEND_PATH, "report.html"))

@app.get("/about.html")
def serve_about():
    return FileResponse(os.path.join(FRONTEND_PATH, "about.html"))

@app.get("/contact.html")
def serve_contact():
    return FileResponse(os.path.join(FRONTEND_PATH, "contact.html"))

@app.get("/legal.html")
def serve_legal():
    return FileResponse(os.path.join(FRONTEND_PATH, "legal.html"))

@app.get("/login.html")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_PATH, "login.html"))


@app.post("/signup")
async def signup(request: Request):
    data = await request.json()
    email = data.get("email")

    existing = supabase.table("users").select("*").eq("email", email).execute()
    if existing.data:
        return {"message": "User already exists"}

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
    if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        return {"message": "Invalid credentials"}

    return {"message": "Login successful"}