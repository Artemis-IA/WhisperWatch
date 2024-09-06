# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import sessionmaker
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Use the async engine for app queries
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=True)

# Use the synchronous engine for schema creation
sync_engine = create_engine(SQLALCHEMY_DATABASE_URL.replace('postgresql+asyncpg', 'postgresql'), echo=True)

Base = declarative_base()

def init_db():
    """ Initialize the database by creating all tables """
    Base.metadata.create_all(bind=sync_engine)  # Use the sync engine for schema creation

async def get_db():
    """ Dependency to get DB session for async queries """
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


