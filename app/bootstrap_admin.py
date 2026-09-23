import argparse
import getpass

from email_validator import validate_email

from app import models
from app.auth_security import hash_password
from app.database import SessionLocal


def parse_args():
    parser = argparse.ArgumentParser(description="Create or update the private LEVERAGE super admin")
    parser.add_argument("--email", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    email = validate_email(args.email, check_deliverability=False).normalized
    password = getpass.getpass("Super admin password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")
    if len(password) < 6:
        raise SystemExit("Password must contain at least 6 characters")

    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            user = models.User(email=email)
            db.add(user)
        user.password_hash = hash_password(password)
        user.role = models.RoleEnum.SUPER_ADMIN
        user.is_verified = True
        user.is_active = True
        user.failed_login_attempts = 0
        user.login_locked_until = None
        user.auth_version = (user.auth_version or 0) + 1
        user.mfa_secret = None
        user.mfa_enabled = False
        user.mfa_recovery_codes = None
        db.commit()
        print(f"Super admin ready: {email}. MFA enrollment is required on first login.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
