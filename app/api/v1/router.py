from fastapi import APIRouter

from app.api.v1 import api_keys, auth, jobs, organizations, service_jobs, webhooks

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(jobs.router)
api_router.include_router(api_keys.router)
api_router.include_router(webhooks.router)
api_router.include_router(service_jobs.router)
