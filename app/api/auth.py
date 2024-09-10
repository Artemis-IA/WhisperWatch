# app/api/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.api.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from app.crud.crud_user import create_user, get_user_by_email

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists.",
        )
    created_user = await create_user(db, user_in)
    return created_user


@router.post("/login", response_model=Token)
async def login(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_email(db, email=form_data.username)
    
    if not user:
        print(f"User with email {form_data.username} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        print(f"Invalid password for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Durée d'expiration du jeton (par exemple, 15 minutes)
    access_token_expires = timedelta(minutes=15)
    
    # Créer un jeton d'accès avec une expiration
    access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    
    print(f"Login successful for user {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}