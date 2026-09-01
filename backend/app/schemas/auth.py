from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from backend.app.core.credentials import PASSWORD_PATTERN, USERNAME_PATTERN
from backend.app.services.password import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH


class RegisterStartRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr

    @field_validator("first_name", "last_name")
    @classmethod
    def names_are_user_input(cls, value: str) -> str:
        if any(ord(character) < 32 or ord(character) == 127 for character in value):
            raise ValueError("Name contains invalid characters")
        value = value.strip()
        if not value:
            raise ValueError("Name is required")
        return value


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(pattern=r"^\d{6}$")


class RegisterCompleteRequest(BaseModel):
    email: EmailStr
    username: str = Field(pattern=USERNAME_PATTERN)
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH, pattern=PASSWORD_PATTERN)
    confirm_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH, pattern=PASSWORD_PATTERN)

    @field_validator("username")
    @classmethod
    def username_is_normalized(cls, value: str) -> str:
        return value.lower()

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    identifier: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
