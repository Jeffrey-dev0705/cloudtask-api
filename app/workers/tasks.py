import time
import uuid
from datetime import UTC, datetime

import httpx

from app.core.webhooks import encode_event, sign_webhook
from app.db.session import SessionLocal
from app.models.job import Job, JobAttempt
from app.models.webhook import Webhook, WebhookDelivery
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=3)
def deliver_webhook(self, delivery_id: str, event: dict):
    db = SessionLocal()
    try:
        delivery = db.get(WebhookDelivery, uuid.UUID(delivery_id))
        if not delivery:
            return {"status": "missing"}
        hook = db.get(Webhook, delivery.webhook_id)
        if not hook or not hook.active:
            delivery.status = "disabled"; db.commit(); return {"status": "disabled"}
        body = encode_event(event)
        signature = sign_webhook(hook.secret, body)
        delivery.attempts += 1
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(hook.url, content=body, headers={"Content-Type":"application/json","X-CloudTask-Event": event["type"],"X-CloudTask-Signature": signature})
            delivery.status_code = response.status_code
            delivery.response_body = response.text[:2000]
            if response.status_code >= 400:
                raise RuntimeError(f"Webhook returned HTTP {response.status_code}")
            delivery.status = "delivered"; delivery.delivered_at = datetime.now(UTC); db.commit()
            return {"status": "delivered", "status_code": response.status_code}
        except Exception as exc:
            delivery.status = "failed"; delivery.last_error = str(exc); db.commit(); raise
    finally:
        db.close()

def enqueue_job_event(db, job: Job, event_type: str):
    hooks = db.query(Webhook).filter(Webhook.organization_id == job.organization_id, Webhook.event_type == event_type, Webhook.active.is_(True)).all()
    event = {"id": str(uuid.uuid4()), "type": event_type, "created_at": datetime.now(UTC).isoformat(), "data": {"job_id": str(job.id), "status": job.status, "job_type": job.job_type}}
    delivery_ids=[]
    for hook in hooks:
        delivery=WebhookDelivery(webhook_id=hook.id,event_id=event["id"])
        db.add(delivery); db.flush(); delivery_ids.append(str(delivery.id))
    db.commit()
    for delivery_id in delivery_ids:
        deliver_webhook.delay(delivery_id, event)

