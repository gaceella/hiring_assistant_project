import os
import uuid
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from backend.ranker import rank_candidates
from backend.question_generator import generate_interview_questions
from backend.cv_parser import parse_cv
from backend.db import init_db, save_job, save_candidate, get_job, get_candidates

app = FastAPI(title="Gaceella AI Hiring Assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class JobDescriptionRequest(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    experience_years: int
    location: str = "Pakistan"

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
def root():
    return {"name": "Gaceella AI Hiring Assistant", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/jobs/create")
def create_job(job: JobDescriptionRequest):
    job_id = str(uuid.uuid4())[:8]
    save_job(job_id, job.dict())
    return {"job_id": job_id, "message": "Job created", "job": job.dict()}

@app.post("/jobs/{job_id}/upload-cvs")
async def upload_cvs(job_id: str, files: List[UploadFile] = File(...), x_api_key: str = Header(...)):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    uploaded = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
        file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        candidate_data          = parse_cv(str(file_path), x_api_key)
        candidate_data["filename"] = file.filename
        save_candidate(job_id, candidate_data)
        uploaded.append(file.filename)

    return {"job_id": job_id, "uploaded": len(uploaded), "files": uploaded}

@app.get("/jobs/{job_id}/rank")
def rank_job_candidates(job_id: str, x_api_key: str = Header(...)):
    job        = get_job(job_id)
    candidates = get_candidates(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")
    ranked = rank_candidates(job, candidates, x_api_key)
    return {"job_id": job_id, "candidates": ranked, "total_candidates": len(ranked)}

@app.get("/jobs/{job_id}/candidates/{candidate_name}/questions")
def get_interview_questions(job_id: str, candidate_name: str, x_api_key: str = Header(...)):
    job        = get_job(job_id)
    candidates = get_candidates(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    candidate = next((c for c in candidates if c.get("name","").lower() == candidate_name.lower()), None)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    questions = generate_interview_questions(job, candidate, x_api_key)
    return {"candidate_name": candidate.get("name"), "job_title": job.get("title"), "questions": questions}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
