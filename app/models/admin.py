from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.future import select
from app.database import Base
from app.utils.security import get_password_hash

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_superadmin = Column(Boolean, default=False)

    @classmethod
    async def create_admin(cls, db, username: str, password: str, is_superadmin: bool = False):
        hashed_password = get_password_hash(password)
        new_admin = cls(username=username, hashed_password=hashed_password, is_superadmin=is_superadmin)
        db.add(new_admin)
        await db.commit()
        await db.refresh(new_admin)
        return new_admin

    @classmethod
    async def get_by_username(cls, db, username: str):
        query = select(cls).where(cls.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def create_superadmin(cls, db, username: str, password: str):
        return await cls.create_admin(db, username, password, is_superadmin=True)