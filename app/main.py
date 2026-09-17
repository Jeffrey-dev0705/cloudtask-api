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

