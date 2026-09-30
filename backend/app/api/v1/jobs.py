from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db import get_db
from ...dependencies import current_user, require_roles
from ...models import Job
from ...schemas import JobCreate

router = APIRouter()


def serialize_job(job: Job):
    skills = job.required_skills.split("||") if "||" in job.required_skills else job.required_skills.split(",")
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "required_skills": [x.strip() for x in skills if x.strip()],
    }


@router.post("", status_code=201)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("OWNER", "ADMIN", "MANAGER", "RECRUITER")),
):
    job = Job(
        organization_id=user.organization_id,
        title=payload.title,
        description=payload.description,
        required_skills="||".join(payload.required_skills),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return serialize_job(job)


@router.get("")
def list_jobs(
    search: str = Query("", max_length=100),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    q = db.query(Job).filter(Job.organization_id == user.organization_id)
    if search.strip():
        q = q.filter(Job.title.ilike(f"%{search.strip()}%"))
    return [serialize_job(j) for j in q.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()]


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.organization_id == user.organization_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    return serialize_job(job)
