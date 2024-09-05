# app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr

# Base schema for users
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

# Schema for creating a user
class UserCreate(UserBase):
    password: str

# Schema for updating a user
class UserUpdate(UserBase):
    password: Optional[str] = None

# Schema for representing a user in responses
class UserDB(UserBase):
    id: int

    class Config:
        from_attributes = True  # For ORM compatibility
