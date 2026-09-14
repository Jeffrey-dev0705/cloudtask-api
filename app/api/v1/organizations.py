from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationResponse

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("", response_model=OrganizationResponse, status_code=201)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if db.query(Organization).filter(Organization.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="Slug already exists")
    organization = Organization(name=payload.name, slug=payload.slug)
    db.add(organization); db.flush()
    db.add(OrganizationMember(organization_id=organization.id, user_id=user.id, role="owner"))
    db.commit(); db.refresh(organization)
    return organization

