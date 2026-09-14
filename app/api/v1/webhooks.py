import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_org_roles
from app.models.webhook import Webhook, WebhookDelivery
from app.schemas.webhook import WebhookCreate, WebhookCreatedResponse, WebhookResponse

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

