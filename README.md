# 🚀 Talentra AI — Intelligent Interview & Resume Evaluation System

## 📌 Overview

**Talentra AI** is an AI-powered hiring assistant that automates resume screening and interview evaluation. It combines **speech-to-text (Whisper)**, **LLM analysis (Gemini)**, and **cloud storage (Supabase)** to provide structured, unbiased candidate insights.

The system supports:

* 📄 Resume-based candidate profiling
* 🎙️ Offline (audio) interview evaluation
* 🎥 Online (video upload) interview evaluation
* 📊 Automated scoring, feedback, and reporting
* 🧠 Persistent candidate reports with database storage

---

## 🎯 Key Features

### 🔹 1. Resume Analysis (Upload Page)

* Upload candidate resume (PDF)
* Extract:

  * Name
  * Email
  * Phone number
  * GitHub & LinkedIn URLs
* Compare with job description
* Generate:

  * Match score (%)
  * Strengths & gaps

---

### 🔹 2. Interview Modes

#### 🟢 Offline Mode

* Records audio via microphone
* Converts audio → text (Groq Whisper)
* Sends transcript → Gemini
* Returns:

  * Technical score
  * Communication score
  * Strengths & gaps
  * Evaluation summary

---

#### 🔵 Online Mode

* Opens Google Meet
* User uploads screen recording after session
* Backend:

  * Extracts audio using `moviepy`
  * Sends audio → Whisper → transcript
  * Sends transcript → Gemini → evaluation

---

### 🔹 3. AI Evaluation

Uses **Gemini API** to generate:

* Technical Score (0–100)
* Communication Score (0–100)
* Strengths & Weaknesses
* Summary
* Recommendation %

---

### 🔹 4. Persistent Reports (Supabase)

Each interview generates a **stored report** containing:

* Candidate details (from resume)
* Job description
* Resume score
* Interview scores
* AI feedback

---

### 🔹 5. Dashboard (Result Page)

* Shows all interviews per user
* Each interview → card view:

  * Name
  * Email
  * Job description
  * Date
* "View Report" → detailed report page

---

### 🔹 6. Full Report Page

Displays:

* Candidate profile
* Resume match %
* Interview scores
* AI-generated summary
* Recommendation
* GitHub & LinkedIn links

---

## 🏗️ Tech Stack

### Frontend

* HTML + Tailwind CSS
* Vanilla JavaScript

### Backend

* FastAPI (Python)

### AI Services

* **Groq Whisper API** → Speech-to-text
* **Google Gemini API** → Analysis

### Database

* Supabase (PostgreSQL)

### Media Processing

* MoviePy (video → audio extraction)

---

## ⚙️ Project Structure

```
talentra/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── ...
│   └── .env
│
├── frontend/
│   ├── pages/
│   │   ├── index.html
│   │   ├── upload.html
│   │   ├── interview.html
│   │   ├── result.html
│   │   ├── report.html
│   │   └── login.html
│   └── assets/
│
└── README.md
```

---

## 🔐 Environment Variables (.env)

Create a `.env` file inside `backend/`:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

---

## 📦 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone <repo-url>
cd talentra
```

---

### 2️⃣ Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Required packages:

* fastapi
* uvicorn
* python-dotenv
* supabase
* bcrypt
* moviepy
* groq
* google-generativeai
* PyPDF2

---

### 3️⃣ Run Server

```bash
uvicorn app.main:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

---

### 4️⃣ Open Frontend

```
http://127.0.0.1:8000/index.html
```

---

## 🔄 Complete Workflow

### 🧩 Step-by-Step Flow

### 1. Resume Upload

* User uploads resume + job description
* Backend:

  * Extracts text (PyPDF2)
  * Sends to Gemini
  * Returns structured JSON
* Frontend:

  * Stores data in `localStorage`

---

### 2. Interview Session

#### Offline:

* Record audio → save blob
* Send to backend

#### Online:

* Upload video → backend extracts audio

---

### 3. Speech-to-Text

* Audio → Groq Whisper
* Returns transcript

---

### 4. AI Evaluation

* Transcript → Gemini
* Returns:

```json
{
  "technical_score": 85,
  "communication_score": 90,
  "strengths": [],
  "gaps": [],
  "evaluation_summary": "",
  "recommendation_percentage": 80
}
```

---

### 5. Database Storage (Supabase)

Saved fields:

* user_email
* name, email, phone
* github, linkedin
* job_description
* resume_score
* interview scores
* strengths, gaps
* summary

---

### 6. Dashboard Rendering

* Fetch `/my-reports`
* Display cards dynamically

---

### 7. Report Page

* Fetch `/report/{id}`
* Populate UI with stored data

---

## 🧠 System Architecture

```
Frontend (HTML + JS)
        ↓
FastAPI Backend
        ↓
 ┌───────────────┐
 │ Whisper (Groq)│ → Transcript
 └───────────────┘
        ↓
 ┌───────────────┐
 │ Gemini (Google)│ → Analysis
 └───────────────┘
        ↓
Supabase Database
        ↓
Frontend UI (Report/Dashboard)
```

---

## ⚠️ Known Limitations

* Large video files (>25MB) are rejected
* Gemini API may return 503 (retry needed)
* Resume parsing depends on PDF quality
* No authentication session management (basic login)

---

## 🔮 Future Improvements

*  Multi-role (HR/Candidate)
*  Google Cloud for video/doc./audio storage
*  Advanced analytics dashboard
*  Integrated Virtual Interview platform

---

## 💡 Key Highlights

✔ Full AI pipeline (Audio → Text → Insight)
✔ Real-time UI updates
✔ Persistent candidate tracking
✔ Modular backend (scalable)
✔ Works for both offline & online interviews

---

## 👨‍💻 Authors

- Souvagya Karmakar  
- Sushmita Roy  
- Anirban Pal  
- Sugata Nayak  

---

## ⭐ Final Note

This project demonstrates a **complete AI hiring workflow**:
from resume screening → interview evaluation → decision support.

It is designed to be:

* Scalable
* Modular
* Real-world applicable

---

If you’ve reached here — you’ve built something seriously powerful 🚀
