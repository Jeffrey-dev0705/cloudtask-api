import uuid
from datetime import UTC, datetime

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.api_keys import hash_api_key
from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.api_key import ApiKey
from app.models.organization import OrganizationMember
from app.models.user import User

bearer = HTTPBearer(auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        payload = decode_token(credentials.credentials, "access")
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User unavailable")
    return user

def get_organization_id(x_organization_id: str = Header(alias="X-Organization-ID"), user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> uuid.UUID:
    try:
        organization_id = uuid.UUID(x_organization_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Organization-ID") from None
    membership = db.query(OrganizationMember).filter(OrganizationMember.organization_id == organization_id, OrganizationMember.user_id == user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    return organization_id

