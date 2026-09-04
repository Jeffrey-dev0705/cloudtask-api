import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, get_organization_id
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse
from app.workers.tasks import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

