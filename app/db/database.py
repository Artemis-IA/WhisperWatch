# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Use the async engine for app queries with connection pooling
async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    future=True, 
    echo=True,
    pool_size=10,  # Adjust based on your needs
    max_overflow=20  # Allow up to 20 extra connections if the pool is full
)

# Use the synchronous engine for schema creation
sync_engine = create_engine(
    SQLALCHEMY_DATABASE_URL.replace('postgresql+asyncpg', 'postgresql'), 
    echo=True
)

async_session = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

def init_db():
    """ Initialize the database by creating all tables """
    Base.metadata.create_all(bind=sync_engine)
async def get_db():
    """ Dependency to get DB session for async queries """
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


