-- Supabase SQL Editor Command --

CREATE TABLE IF NOT EXISTS public.reports (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    name TEXT,
    email TEXT,
    phone TEXT,
    github_url TEXT,
    linkedin_url TEXT,
    job_description TEXT,
    resume_score INTEGER DEFAULT 0,
    technical_score INTEGER DEFAULT 0,
    communication_score INTEGER DEFAULT 0,
    strengths JSONB,
    gaps JSONB,
    evaluation_summary TEXT,
    recommendation_percentage INTEGER DEFAULT 0,
    recommendation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS and setup policies as needed depending on your environment
-- ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
