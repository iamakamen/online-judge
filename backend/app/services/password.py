from pwdlib import PasswordHash

from backend.app.core.credentials import PASSWORD_ALLOWED_CHARACTERS

password_hash = PasswordHash.recommended()

PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 24


def validate_password(password: str) -> None:
    if not password:
        raise ValueError("Password is required")
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError("Password must be at least 12 characters")
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValueError("Password must not exceed 24 characters")
    if not all(character in PASSWORD_ALLOWED_CHARACTERS for character in password):
        raise ValueError("Password contains invalid characters")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)
