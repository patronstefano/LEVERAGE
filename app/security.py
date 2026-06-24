from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.database import get_db


SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def create_token(
    user: models.User,
    token_type: str = "access",
    mfa_verified: bool = False,
    expires_delta: Optional[timedelta] = None,
) -> str:
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": user.email,
        "type": token_type,
        "ver": user.auth_version,
        "mfa": mfa_verified,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise credentials_exception from exc
    if payload.get("sub") is None or payload.get("type") != expected_type:
        raise credentials_exception
    return payload


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def authenticated_user_from_payload(db: Session, payload: dict) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_user_by_email(db, str(payload["sub"]))
    if (
        user is None
        or not user.is_active
        or not user.is_verified
        or payload.get("ver") != user.auth_version
    ):
        raise credentials_exception
    setattr(user, "_token_mfa_verified", bool(payload.get("mfa")))
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    return authenticated_user_from_payload(db, decode_token(token))


def get_optional_current_user(
    token: Optional[str] = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    if not token:
        return None
    try:
        payload = decode_token(token)
        return authenticated_user_from_payload(db, payload)
    except HTTPException:
        return None


def get_mfa_setup_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    user = authenticated_user_from_payload(db, decode_token(token, expected_type="mfa_setup"))
    if user.role not in {models.RoleEnum.ADMIN, models.RoleEnum.SUPER_ADMIN}:
        raise HTTPException(status_code=403, detail="MFA setup is reserved for admin accounts")
    return user


def get_current_admin_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role not in {models.RoleEnum.ADMIN, models.RoleEnum.SUPER_ADMIN}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can perform this action",
        )
    if not current_user.mfa_enabled or not getattr(current_user, "_token_mfa_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access requires verified MFA",
        )
    return current_user


def get_current_super_admin_user(
    current_user: models.User = Depends(get_current_admin_user),
) -> models.User:
    if current_user.role != models.RoleEnum.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin users can perform this action",
        )
    return current_user
