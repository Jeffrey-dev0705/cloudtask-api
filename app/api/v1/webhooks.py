import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_org_roles
from app.models.webhook import Webhook, WebhookDelivery
from app.schemas.webhook import WebhookCreate, WebhookCreatedResponse, WebhookResponse

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("", response_model=WebhookCreatedResponse, status_code=201)
def create_webhook(
    payload: WebhookCreate,
    db: Session = Depends(get_db),
    organization_id: uuid.UUID = Depends(require_org_roles("owner", "admin")),
):
    secret = secrets.token_urlsafe(32)
    item = Webhook(organization_id=organization_id, url=str(payload.url), secret=secret, event_type=payload.event_type)
    db.add(item); db.commit(); db.refresh(item)
    return WebhookCreatedResponse(id=str(item.id), url=item.url, event_type=item.event_type, active=item.active, created_at=item.created_at, secret=secret)

@router.get("", response_model=list[WebhookResponse])
def list_webhooks(
    db: Session = Depends(get_db),
    organization_id: uuid.UUID = Depends(require_org_roles("owner", "admin")),
):
    return db.query(Webhook).filter(Webhook.organization_id == organization_id).order_by(Webhook.created_at.desc()).all()

@router.delete("/{webhook_id}", status_code=204)
def disable_webhook(
    webhook_id: uuid.UUID,
    db: Session = Depends(get_db),
    organization_id: uuid.UUID = Depends(require_org_roles("owner", "admin")),
):
    item = db.query(Webhook).filter(Webhook.id == webhook_id, Webhook.organization_id == organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Webhook not found")
    item.active = False; db.commit()

