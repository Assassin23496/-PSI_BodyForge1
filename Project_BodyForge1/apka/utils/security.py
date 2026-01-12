"""Helper functions for password hashing and JWT token generation."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

JWT_SECRET_KEY = "CHANGE_ME_SUPER_SECRET"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 24h

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def normalize_email(email: str) -> str:
    """Normalize email: trim and lowercase."""
    return email.strip().lower()


def hash_password(password: str) -> str:
    """Generate a password hash (bcrypt)."""
    return _pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return _pwd_context.verify(password, hashed)


def create_access_token(subject: str) -> str:
    """Create a signed JWT token with `sub` = subject."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=JWT_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
