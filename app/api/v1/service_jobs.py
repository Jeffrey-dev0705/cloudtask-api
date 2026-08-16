from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import authenticate_api_key, get_db
from app.models.api_key import ApiKey
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse
from app.workers.tasks import process_job

router = APIRouter(prefix="/service/jobs", tags=["service-jobs"])

@router.post("", response_model=JobResponse, status_code=201)
def create_service_job(payload: JobCreate, db: Session = Depends(get_db), api_key: ApiKey = Depends(authenticate_api_key)):
    # API keys have no user id; attribute created_by to an org member until a service principal exists.
    from app.models.organization import OrganizationMember
    owner = db.query(OrganizationMember).filter(OrganizationMember.organization_id == api_key.organization_id).order_by(OrganizationMember.role.asc()).first()
    job = Job(organization_id=api_key.organization_id, created_by=owner.user_id, job_type=payload.job_type, priority=payload.priority, payload=payload.payload, max_attempts=payload.max_attempts)
    db.add(job); db.commit(); db.refresh(job); process_job.delay(str(job.id)); return job
