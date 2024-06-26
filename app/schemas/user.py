from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    phone: str

class UserCreate(UserBase):
    password: str
    name: str
    age: int
    weight: float
    height: float
    gender: str
    activity_level: str
    allergies: Optional[str] = None

class User(UserBase):
    id: int
    name: str
    weight: float
    height: float
    age: int
    gender: str
    activity_level: str
    allergies: Optional[str] = None

    class Config:
        orm_mode = True
class UserUpdate(BaseModel):
    name: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    allergies: Optional[str] = None

class UserResponse(BaseModel):
    user: User
    access_token: str
    token_type: str