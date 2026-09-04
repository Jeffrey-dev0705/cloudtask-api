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

