from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

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