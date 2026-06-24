import hashlib
import json
import secrets
from typing import Optional

import pyotp
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError


password_hasher = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password_hash: Optional[str], password: str) -> bool:
    if not password_hash:
        return False
    try:
        return password_hasher.verify(password_hash, password)
    except (InvalidHashError, VerifyMismatchError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    return password_hasher.check_needs_rehash(password_hash)


def generate_email_token() -> str:
    return secrets.token_urlsafe(32)


def hash_email_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_mfa_secret() -> str:
    return pyotp.random_base32()


def build_mfa_provisioning_uri(secret: str, email: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name="LEVERAGE")


def generate_recovery_codes(count: int = 8) -> list[str]:
    return [f"{secrets.token_hex(4)}-{secrets.token_hex(4)}" for _ in range(count)]


def hash_recovery_codes(codes: list[str]) -> str:
    return json.dumps([hash_password(code) for code in codes])


def verify_mfa_code(secret: Optional[str], recovery_codes: Optional[str], code: str) -> tuple[bool, Optional[str]]:
    normalized = code.strip().replace(" ", "")
    if secret and normalized.isdigit() and pyotp.TOTP(secret).verify(normalized, valid_window=1):
        return True, recovery_codes

    try:
        stored_hashes = json.loads(recovery_codes or "[]")
    except json.JSONDecodeError:
        stored_hashes = []
    for index, stored_hash in enumerate(stored_hashes):
        if verify_password(stored_hash, normalized):
            remaining = stored_hashes[:index] + stored_hashes[index + 1:]
            return True, json.dumps(remaining)
    return False, recovery_codes
