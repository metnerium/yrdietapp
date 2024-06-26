# app/models/user.py
from sqlalchemy import Column, Integer, String, Float, Boolean, select
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    nickname = Column(String, unique=True, index=True, nullable=False)  # Changed to non-nullable
    hashed_password = Column(String, nullable=True)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    gender = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)
    allergies = Column(String, nullable=True)
    sms_code = Column(String, nullable=True)
    is_phone_verified = Column(Boolean, default=False)

    posts = relationship("Post", back_populates="user")
    recipes = relationship("Recipe", back_populates="user")

    @classmethod
    async def get_by_phone(cls, db, phone):
        query = select(cls).where(cls.phone == phone)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_nickname(cls, db, nickname):
        query = select(cls).where(cls.nickname == nickname)
        result = await db.execute(query)
        return result.scalar_one_or_none()