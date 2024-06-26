from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from app.database import Base
from datetime import datetime
import pytz


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    gender = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)
    allergies = Column(String, nullable=True)
    posts = relationship("Post", back_populates="user")

    # Updated fields for SMS verification
    sms_code = Column(String, nullable=True)
    is_phone_verified = Column(Boolean, default=False)

    @classmethod
    async def get_by_phone(cls, db: AsyncSession, phone: str):
        query = select(cls).where(cls.phone == phone)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def get_current_time():
        return datetime.now(pytz.UTC)

