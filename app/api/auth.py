# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.api.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from app.core.user_manager import UserManager, get_user_manager

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db), 
    user_manager: UserManager = Depends(get_user_manager)
):
    user = await crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    created_user = await user_manager.create(user_create=user_in)
    return created_user


@router.post("/login", response_model=Token)
async def login(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
