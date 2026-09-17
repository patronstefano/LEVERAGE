from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth_security import (
    build_mfa_provisioning_uri,
    generate_email_token,
    generate_mfa_secret,
    generate_recovery_codes,
    hash_email_token,
    hash_password,
    hash_recovery_codes,
    password_needs_rehash,
    verify_mfa_code,
    verify_password,
)
from app.config import settings
from app.database import get_db
from app.email_utils import send_email
from app.rate_limit import enforce_rate_limit
from app.security import (
    create_token,
    get_current_user,
    get_mfa_setup_user,
    get_user_by_email,
)


router = APIRouter()
GENERIC_REGISTRATION_MESSAGE = "If the address can be registered, a verification email will be sent."
GENERIC_RESET_MESSAGE = "If the address exists, password reset instructions will be sent."
DUMMY_PASSWORD_HASH = hash_password("LEVERAGE-dummy-password-not-used")
DEMO_USER_EMAIL = "demo.user@leverage-demo.com"
DEMO_ADMIN_EMAIL = "demo.admin@leverage-demo.com"
DEMO_SUPER_ADMIN_EMAIL = "demo.superadmin@leverage-demo.com"
DEMO_PASSWORD_HASH = hash_password("LEVERAGE-demo-login-disabled-password")


def email_cooldown_active(last_sent_at: Optional[datetime]) -> bool:
    if last_sent_at is None:
        return False
    return last_sent_at > datetime.utcnow() - timedelta(seconds=settings.auth_email_cooldown_seconds)


def send_verification_email(user: models.User, db: Session) -> None:
    if email_cooldown_active(user.email_verification_sent_at):
        return
    token = generate_email_token()
    user.email_verification_token_hash = hash_email_token(token)
    user.email_verification_expires_at = datetime.utcnow() + timedelta(
        minutes=settings.email_token_expire_minutes
    )
    user.email_verification_sent_at = datetime.utcnow()
    db.add(user)
    db.commit()
    link = f"{settings.frontend_base_url.rstrip('/')}/verify-email?token={token}"
    if not send_email(
        "Verify your LEVERAGE email",
        f"Verify your LEVERAGE account using this link:\n\n{link}\n\n"
        f"The link expires in {settings.email_token_expire_minutes} minutes.",
        user.email,
    ):
        raise HTTPException(status_code=503, detail="Email delivery is temporarily unavailable")


def send_password_reset_email(user: models.User, db: Session) -> None:
    if email_cooldown_active(user.password_reset_sent_at):
        return
    token = generate_email_token()
    user.password_reset_token_hash = hash_email_token(token)
    user.password_reset_expires_at = datetime.utcnow() + timedelta(
        minutes=settings.password_reset_expire_minutes
    )
    user.password_reset_sent_at = datetime.utcnow()
    db.add(user)
    db.commit()
    link = f"{settings.frontend_base_url.rstrip('/')}/reset-password?token={token}"
    if not send_email(
        "Reset your LEVERAGE password",
        f"Reset your LEVERAGE password using this link:\n\n{link}\n\n"
        f"The link expires in {settings.password_reset_expire_minutes} minutes.",
        user.email,
    ):
        raise HTTPException(status_code=503, detail="Email delivery is temporarily unavailable")


def register_failed_login(user: models.User, db: Session) -> None:
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= settings.max_login_attempts:
        user.login_locked_until = datetime.utcnow() + timedelta(minutes=settings.login_lock_minutes)
    db.add(user)
    db.commit()


def reset_failed_login(user: models.User, db: Session) -> None:
    user.failed_login_attempts = 0
    user.login_locked_until = None
    db.add(user)
    db.commit()


def demo_login_allowed() -> bool:
    return settings.app_env.lower() == "development"


def get_or_create_demo_user(db: Session, role: models.RoleEnum) -> models.User:
    demo_emails = {
        models.RoleEnum.USER: DEMO_USER_EMAIL,
        models.RoleEnum.ADMIN: DEMO_ADMIN_EMAIL,
        models.RoleEnum.SUPER_ADMIN: DEMO_SUPER_ADMIN_EMAIL,
    }
    email = demo_emails[role]
    user = get_user_by_email(db, email)
    if not user:
        user = models.User(
            email=email,
            password_hash=DEMO_PASSWORD_HASH,
            role=role,
            preferred_language=models.LanguageEnum.EN,
            is_verified=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    user.role = role
    user.is_verified = True
    user.is_active = True
    user.login_locked_until = None
    user.failed_login_attempts = 0
    if role in {models.RoleEnum.ADMIN, models.RoleEnum.SUPER_ADMIN}:
        user.mfa_secret = user.mfa_secret or generate_mfa_secret()
        user.mfa_enabled = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=schemas.AuthMessage, status_code=202)
def register(
    payload: schemas.UserRegister,
    request: Request,
    db: Session = Depends(get_db),
):
    enforce_rate_limit(request, "register", limit=5, window_seconds=300, subject=payload.email)
    existing_user = get_user_by_email(db, payload.email)
    if existing_user:
        if not existing_user.is_verified and existing_user.is_active:
            send_verification_email(existing_user, db)
        return schemas.AuthMessage(message=GENERIC_REGISTRATION_MESSAGE)

    user = models.User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=models.RoleEnum.USER,
        preferred_language=models.LanguageEnum(payload.preferred_language.value),
        is_verified=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    send_verification_email(user, db)
    return schemas.AuthMessage(message=GENERIC_REGISTRATION_MESSAGE)


@router.post("/demo-login", response_model=schemas.LoginResponse)
def demo_login(
    payload: schemas.DemoLoginRequest,
    db: Session = Depends(get_db),
):
    if not demo_login_allowed():
        raise HTTPException(status_code=404, detail="Not found")
    if payload.role not in {schemas.RoleEnum.USER, schemas.RoleEnum.ADMIN, schemas.RoleEnum.SUPER_ADMIN}:
        raise HTTPException(status_code=400, detail="Demo login supports user, admin or super_admin only")

    role = models.RoleEnum(payload.role.value)
    user = get_or_create_demo_user(db, role)
    return schemas.LoginResponse(
        access_token=create_token(
            user,
            mfa_verified=role in {models.RoleEnum.ADMIN, models.RoleEnum.SUPER_ADMIN},
        ),
    )


@router.post("/verify-email", response_model=schemas.AuthMessage)
def verify_email(payload: schemas.EmailTokenRequest, db: Session = Depends(get_db)):
    token_hash = hash_email_token(payload.token)
    user = db.query(models.User).filter(
        models.User.email_verification_token_hash == token_hash,
    ).first()
    if (
        user is None
        or user.email_verification_expires_at is None
        or user.email_verification_expires_at < datetime.utcnow()
        or not user.is_active
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")
    user.is_verified = True
    user.email_verification_token_hash = None
    user.email_verification_expires_at = None
    db.add(user)
    db.commit()
    return schemas.AuthMessage(message="Email verified successfully")


@router.post("/resend-verification", response_model=schemas.AuthMessage, status_code=202)
def resend_verification(
    payload: schemas.EmailAddressRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    enforce_rate_limit(request, "resend-verification", limit=5, window_seconds=300, subject=payload.email)
    user = get_user_by_email(db, payload.email)
    if user and user.is_active and not user.is_verified:
        send_verification_email(user, db)
    return schemas.AuthMessage(message=GENERIC_REGISTRATION_MESSAGE)


@router.post("/login", response_model=schemas.LoginResponse)
def login(
    payload: schemas.LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    enforce_rate_limit(request, "login", limit=20, window_seconds=300, subject=payload.email)
    user = get_user_by_email(db, payload.email)
    if user is None:
        verify_password(DUMMY_PASSWORD_HASH, payload.password)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if user.login_locked_until and user.login_locked_until > datetime.utcnow():
        raise HTTPException(status_code=429, detail="Account temporarily locked. Try again later.")
    if not user.is_active or not verify_password(user.password_hash, payload.password):
        if user.is_active:
            register_failed_login(user, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email verification required")

    if user.password_hash and password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)
        db.add(user)

    is_admin = user.role in {models.RoleEnum.ADMIN, models.RoleEnum.SUPER_ADMIN}
    if is_admin and not user.mfa_enabled:
        reset_failed_login(user, db)
        setup_token = create_token(
            user,
            token_type="mfa_setup",
            expires_delta=timedelta(minutes=10),
        )
        return schemas.LoginResponse(
            mfa_setup_required=True,
            mfa_setup_token=setup_token,
        )
    if is_admin:
        if not payload.mfa_code:
            return schemas.LoginResponse(mfa_required=True)
        valid, remaining_codes = verify_mfa_code(
            user.mfa_secret,
            user.mfa_recovery_codes,
            payload.mfa_code,
        )
        if not valid:
            register_failed_login(user, db)
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        if remaining_codes != user.mfa_recovery_codes:
            user.mfa_recovery_codes = remaining_codes
            db.add(user)
        reset_failed_login(user, db)
    else:
        reset_failed_login(user, db)

    return schemas.LoginResponse(
        access_token=create_token(user, mfa_verified=is_admin),
    )


@router.post("/password/forgot", response_model=schemas.AuthMessage, status_code=202)
def forgot_password(
    payload: schemas.EmailAddressRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    enforce_rate_limit(request, "forgot-password", limit=5, window_seconds=300, subject=payload.email)
    user = get_user_by_email(db, payload.email)
    if user and user.is_active and user.is_verified:
        send_password_reset_email(user, db)
    return schemas.AuthMessage(message=GENERIC_RESET_MESSAGE)


@router.post("/password/reset", response_model=schemas.AuthMessage)
def reset_password(payload: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    token_hash = hash_email_token(payload.token)
    user = db.query(models.User).filter(models.User.password_reset_token_hash == token_hash).first()
    if (
        user is None
        or user.password_reset_expires_at is None
        or user.password_reset_expires_at < datetime.utcnow()
        or not user.is_active
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired password reset link")
    user.password_hash = hash_password(payload.new_password)
    user.password_reset_token_hash = None
    user.password_reset_expires_at = None
    user.failed_login_attempts = 0
    user.login_locked_until = None
    user.auth_version += 1
    db.add(user)
    db.commit()
    return schemas.AuthMessage(message="Password reset successfully")


@router.post("/password/change", response_model=schemas.AuthMessage)
def change_password(
    payload: schemas.PasswordChangeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(current_user.password_hash, payload.current_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(payload.new_password)
    current_user.auth_version += 1
    db.add(current_user)
    db.commit()
    return schemas.AuthMessage(message="Password changed successfully. Please sign in again.")


@router.post("/mfa/setup", response_model=schemas.MFASetupResponse)
def setup_mfa(
    current_user: models.User = Depends(get_mfa_setup_user),
    db: Session = Depends(get_db),
):
    if current_user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA is already enabled")
    if not current_user.mfa_secret:
        current_user.mfa_secret = generate_mfa_secret()
        db.add(current_user)
        db.commit()
    return schemas.MFASetupResponse(
        secret=current_user.mfa_secret,
        provisioning_uri=build_mfa_provisioning_uri(current_user.mfa_secret, current_user.email),
    )


@router.post("/mfa/confirm", response_model=schemas.MFAConfirmResponse)
def confirm_mfa(
    payload: schemas.MFAConfirmRequest,
    current_user: models.User = Depends(get_mfa_setup_user),
    db: Session = Depends(get_db),
):
    valid, _ = verify_mfa_code(current_user.mfa_secret, None, payload.code)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid MFA code")
    recovery_codes = generate_recovery_codes()
    current_user.mfa_enabled = True
    current_user.mfa_recovery_codes = hash_recovery_codes(recovery_codes)
    db.add(current_user)
    db.commit()
    return schemas.MFAConfirmResponse(
        access_token=create_token(current_user, mfa_verified=True),
        token_type="bearer",
        recovery_codes=recovery_codes,
    )


@router.get("/me", response_model=schemas.UserRead)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user
