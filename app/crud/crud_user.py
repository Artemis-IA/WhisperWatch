# crud_user.py
from sqlalchemy.ext.asyncio import AsyncSession, select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

async def get_user(db: AsyncSession, user_id: int):
    return await db.execute(select(User).where(User.id == user_id))

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        email=user.email,
        hashed_password=user.password,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, db_user: User, user_update: UserUpdate):
    for var, value in vars(user_update).items():
        setattr(db_user, var, value) if value else None
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    await db.delete(user)
    await db.commit()
    return user