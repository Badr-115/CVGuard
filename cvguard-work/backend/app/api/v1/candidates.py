from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ...db import get_db
from ...dependencies import current_user, require_roles
from ...models import Candidate, Job
from ...services.files import save_resume
from ...services.scoring import explain_score

router = APIRouter()


def serialize_candidate(candidate: Candidate):
    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "score": candidate.score,
        "resume_uploaded": bool(candidate.resume_path),
    }


@router.post("", status_code=201)
async def create_candidate(
    name: str = Form(..., min_length=2, max_length=200),
    email: str = Form(..., max_length=255),
    phone: str = Form("", max_length=80),
    job_id: int | None = Form(None),
    resume: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user=Depends(require_roles("OWNER", "ADMIN", "MANAGER", "RECRUITER")),
):
    name = " ".join(name.split())
    email = email.strip().lower()
    if "@" not in email or len(email) > 255:
        raise HTTPException(422, "A valid email address is required")

    job = None
    if job_id is not None:
        job = db.query(Job).filter(Job.id == job_id, Job.organization_id == user.organization_id).first()
        if not job:
            raise HTTPException(404, "Job not found")

    path = None
    text = ""
    if resume:
        path, text = await save_resume(resume)

    score = None
    if job:
        skills = job.required_skills.split("||") if "||" in job.required_skills else job.required_skills.split(",")
        skills = [x.strip() for x in skills if x.strip()]
        score = explain_score(text, skills, job.description)["score"]

    candidate = Candidate(
        organization_id=user.organization_id,
        name=name,
        email=email,
        phone=phone.strip(),
        resume_path=path,
        resume_text=text,
        score=score,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return serialize_candidate(candidate)


@router.get("")
def list_candidates(
    search: str = Query("", max_length=100),
    min_score: float | None = Query(None, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    q = db.query(Candidate).filter(Candidate.organization_id == user.organization_id)
    if search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(Candidate.name.ilike(term) | Candidate.email.ilike(term))
    if min_score is not None:
        q = q.filter(Candidate.score >= min_score)
    return [serialize_candidate(c) for c in q.order_by(Candidate.created_at.desc()).offset(offset).limit(limit).all()]


@router.get("/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.organization_id == user.organization_id,
    ).first()
    if not candidate:
        raise HTTPException(404, "Candidate not found")
    return {
        **serialize_candidate(candidate),
        "resume_text_available": bool(candidate.resume_text.strip()),
    }
