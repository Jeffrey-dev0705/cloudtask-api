import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, get_organization_id
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse
from app.workers.tasks import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=JobResponse, status_code=201)
def create_job(payload: JobCreate, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), db: Session = Depends(get_db), user: User = Depends(get_current_user), organization_id: uuid.UUID = Depends(get_organization_id)):
    if idempotency_key:
        existing = db.query(Job).filter(Job.organization_id == organization_id, Job.idempotency_key == idempotency_key).first()
        if existing:
            return existing
    job = Job(organization_id=organization_id, created_by=user.id, idempotency_key=idempotency_key, job_type=payload.job_type, priority=payload.priority, payload=payload.payload, max_attempts=payload.max_attempts)
    db.add(job); db.commit(); db.refresh(job)
    process_job.delay(str(job.id))
    return job

@router.get("", response_model=list[JobResponse])
def list_jobs(status: str | None = Query(default=None), limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db), organization_id: uuid.UUID = Depends(get_organization_id)):
    query = db.query(Job).filter(Job.organization_id == organization_id)
    if status:
        query = query.filter(Job.status == status)
    return query.order_by(Job.created_at.desc()).limit(limit).all()

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db), organization_id: uuid.UUID = Depends(get_organization_id)):
    job = db.query(Job).filter(Job.id == job_id, Job.organization_id == organization_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

