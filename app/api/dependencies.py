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

