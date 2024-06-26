# app/schemas/user.py
from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    phone: str
    nickname: str
    name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    allergies: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, min_length=3, max_length=20)
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    weight: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    allergies: Optional[str] = None

class UserInDB(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    user: UserInDB
    access_token: str
    token_type: str