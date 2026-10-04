import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class UserSignup(BaseModel):
    email: str = Field(..., json_schema_extra={"example": "alex@example.com"})
    password: str = Field(..., min_length=6, max_length=72, json_schema_extra={"example": "Secret123!"})
    fullName: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Alex Mercer"})

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email address format.")
        return clean

class UserLogin(BaseModel):
    email: str = Field(..., json_schema_extra={"example": "alex@example.com"})
    password: str = Field(..., min_length=1, max_length=72, json_schema_extra={"example": "Secret123!"})

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email address format.")
        return clean

class UserResponse(BaseModel):
    id: str
    email: str
    fullName: str
    avatarUrl: Optional[str] = None
    createdAt: Optional[str] = None

class TokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: UserResponse
