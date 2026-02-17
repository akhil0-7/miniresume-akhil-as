from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from datetime import date
from uuid import uuid4
from typing import Optional
import os
import shutil


app = FastAPI()
candidates = [] #Storage

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/health",status_code=200)
def health():
    return {"Status" : "Healthy"}

@app.post("/candidates", status_code=201)
async def upload_candidate(
    full_name: str = Form(...),
    dob: date = Form(...),
    contact_number: str = Form(...),
    contact_address: str = Form(...),
    education_qualification: str = Form(...),
    graduation_year: int = Form(...),
    years_of_experience: int = Form(...),
    skill_set: str = Form(...),
    resume: UploadFile = File(...)
):

    allowed_extensions = ["pdf", "doc", "docx"]
    file_extension = resume.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400)

    candidate_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{candidate_id}.{file_extension}")

    with open(file_path, "wb") as buff:
        shutil.copyfileobj(resume.file, buff)

    candidate_data = {
        "id": candidate_id,
        "full_name": full_name,
        "dob": dob,
        "contact_number": contact_number,
        "contact_address": contact_address,
        "education_qualification": education_qualification,
        "graduation_year": graduation_year,
        "years_of_experience": years_of_experience,
        "skill_set": [skill.strip() for skill in skill_set.split(",")],
        "resume_file": file_path
    }

    candidates.append(candidate_data)

    return {
        "message": "Candidate uploaded successfully",
        "data": candidate_data
    }


@app.get("/candidates", status_code=200)
def list_candidates(
    skill: Optional[str] = None,
    experience: Optional[int] = None,
    graduation_year: Optional[int] = None
):
    
    filtered = candidates

    if skill:
        filtered = [
            c for c in filtered
            if skill.lower() in [s.lower() for s in c["skill_set"]]
        ]
    if experience:
        filtered = [
            c for c in filtered
            if c["years_of_experience"] >= experience
        ]
    if graduation_year:
        filtered = [
            c for c in filtered
            if c["graduation_year"] == graduation_year
        ]
    return {
        "count": len(filtered),
        "data": filtered
    }

@app.get("/candidates/{candidate_id}", status_code=200)
def get_candidate(candidate_id: str):

    for candidate in candidates:
        if candidate["id"] == candidate_id:
            return candidate
    raise HTTPException(status_code=404)

@app.delete("/candidates/{candidate_id}", status_code=200)
def delete_candidate(candidate_id: str):
    for candidate in candidates:
         if candidate["id"] == candidate_id:
            candidates.remove(candidate)
            return {"message": "Candidate deleted Successfully"}
    raise HTTPException(status_code=404)