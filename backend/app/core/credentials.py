import re


USERNAME_PATTERN = r"^[A-Za-z0-9]{8,16}$"
USERNAME_RE = re.compile(USERNAME_PATTERN)
PASSWORD_PATTERN = r"^[A-Za-z0-9!@#$%^&*()]+$"
PASSWORD_ALLOWED_CHARACTERS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
)
