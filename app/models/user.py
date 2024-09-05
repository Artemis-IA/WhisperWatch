# app/models/user.py
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String, Boolean
from app.db.database import Base

# Define the User model with an explicit table name
class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"  # Table name

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    full_name = Column(String, index=True)  # Additional field for full name
