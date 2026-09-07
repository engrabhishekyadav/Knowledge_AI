from typing import Optional
from pydantic import BaseModel, Field

class UserSignup(BaseModel):
    email: str = Field(..., example="alex@example.com")
    password: str = Field(..., min_length=6, example="Secret123!")
    fullName: str = Field(..., min_length=2, example="Alex Mercer")

class UserLogin(BaseModel):
    email: str = Field(..., example="alex@example.com")
    password: str = Field(..., example="Secret123!")

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
