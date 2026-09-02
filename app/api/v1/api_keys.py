import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_org_roles
from app.core.api_keys import generate_api_key
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreatedResponse, ApiKeyResponse

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

@router.post("", response_model=ApiKeyCreatedResponse, status_code=201)
def create_api_key(
    payload: ApiKeyCreate,
    db: Session = Depends(get_db),
    organization_id: uuid.UUID = Depends(require_org_roles("owner", "admin")),
):
    raw, prefix, digest = generate_api_key()
    item = ApiKey(organization_id=organization_id, name=payload.name, key_prefix=prefix, key_hash=digest, expires_at=payload.expires_at)
    db.add(item); db.commit(); db.refresh(item)
    return ApiKeyCreatedResponse(id=str(item.id), name=item.name, key_prefix=item.key_prefix, secret=raw, expires_at=item.expires_at)

@router.get("", response_model=list[ApiKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    organization_id: uuid.UUID = Depends(require_org_roles("owner", "admin")),
):
    return db.query(ApiKey).filter(ApiKey.organization_id == organization_id).order_by(ApiKey.created_at.desc()).all()

@router.delete("/{key_id}", status_code=204)
def revoke_api_key(
    key_id: uuid.UUID,
    db: Session = Depends(get_db),
    organization_id: uuid.UUID = Depends(require_org_roles("owner", "admin")),
):
    item = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.organization_id == organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="API key not found")
    item.active = False; db.commit()
