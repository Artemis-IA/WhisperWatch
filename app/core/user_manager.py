# app/core/user_manager.py
from fastapi_users import BaseUserManager, IntegerIDMixin, FastAPIUsers
from fastapi_users.authentication import JWTStrategy, BearerTransport, AuthenticationBackend
from fastapi import Depends
from app.models.user import User
from app.schemas.user import UserDB, UserCreate
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

# Correctly set up the database for FastAPI Users by passing User model and db session
def get_user_db(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyUserDatabase(User, db)

class UserManager(IntegerIDMixin, BaseUserManager[UserDB, int]):
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    async def on_after_register(self, user: UserDB, request=None):
        print(f"User {user.id} has registered.")

    async def create(self, user_create: UserCreate, safe: bool = False, request=None) -> UserDB:
        hashed_password = get_password_hash(user_create.password)
        
        # Convert the UserCreate object to a dictionary of fields
        create_dict = {
            "email": user_create.email,
            "hashed_password": hashed_password,
            "is_active": user_create.is_active,
            "is_superuser": user_create.is_superuser,
            "full_name": user_create.full_name
        }
        
        # Save the user using SQLAlchemyUserDatabase
        created_user = await self.user_db.create(create_dict)
        return created_user

# Dependency injection for the UserManager
def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    return UserManager(user_db)

# JWT Strategy and Backend
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.JWT_SECRET, lifetime_seconds=3600)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_backend = AuthenticationBackend(name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy)

# Create FastAPI Users instance
fastapi_users = FastAPIUsers[UserDB, int](get_user_manager, [auth_backend])
