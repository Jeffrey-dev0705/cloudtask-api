import time
import uuid

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.rate_limit import fixed_window_limit, redis_client
from app.db.session import SessionLocal

settings=get_settings()
REQUEST_COUNT=Counter("http_requests_total","Total HTTP requests",["method","path","status"])
REQUEST_LATENCY=Histogram("http_request_duration_seconds","HTTP request latency",["method","path"])
app=FastAPI(title=settings.app_name,version="0.2.0",description="Multi-tenant async job API.")

@app.middleware("http")
async def request_context(request: Request, call_next):
    if request.url.path not in {"/health","/ready","/metrics"}:
        await fixed_window_limit(request)
    request_id=request.headers.get("X-Request-ID",str(uuid.uuid4())); start=time.perf_counter()
    response=await call_next(request)
    duration=time.perf_counter()-start; route=request.scope.get("route"); path=getattr(route,"path",request.url.path)
    REQUEST_COUNT.labels(request.method,path,response.status_code).inc(); REQUEST_LATENCY.labels(request.method,path).observe(duration)
    response.headers["X-Request-ID"]=request_id; return response

