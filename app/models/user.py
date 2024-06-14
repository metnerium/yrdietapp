from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    name = Column(String)
    age = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    gender = Column(String)
    activity_level = Column(String)
    allergies = Column(String, nullable=True)
    hashed_password = Column(String)
    posts = relationship("Post", back_populates="user")
    @classmethod
    async def get_by_phone(cls, db: AsyncSession, phone: str):
        query = select(cls).where(cls.phone == phone)
        result = await db.execute(query)
        return result.scalar()