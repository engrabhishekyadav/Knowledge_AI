import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserSignup, UserLogin, TokenResponse, UserResponse
from app.services.auth import (
    hash_password, 
    verify_password, 
    create_access_token, 
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse)
async def signup(
    user_in: UserSignup,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account with hashed password and return access token.
    """
    normalized_email = user_in.email.strip().lower()
    
    # Check if email is already taken
    stmt = select(User).where(User.email == normalized_email)
    res = await db.execute(stmt)
    existing_user = res.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Hash password and create user
    hashed = hash_password(user_in.password)
    user_id = f"user-{uuid.uuid4().hex[:8]}"
    new_user = User(
        id=user_id,
        email=normalized_email,
        full_name=user_in.fullName.strip(),
        hashed_password=hashed,
        avatar_url=f"https://api.dicebear.com/7.x/bottts/svg?seed={normalized_email}"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate JWT access token
    access_token = create_access_token({"sub": new_user.id, "email": new_user.email})

    return {
        "accessToken": access_token,
        "tokenType": "bearer",
        "user": new_user.to_dict()
    }

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user with email and password and return access token.
    """
    normalized_email = credentials.email.strip().lower()
    
    stmt = select(User).where(User.email == normalized_email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    access_token = create_access_token({"sub": user.id, "email": user.email})

    return {
        "accessToken": access_token,
        "tokenType": "bearer",
        "user": user.to_dict()
    }

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve currently authenticated user profile.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated or token expired."
        )
    return current_user.to_dict()
