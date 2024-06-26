from pydantic import BaseModel, Field
from typing import Optional

class PhoneNumber(BaseModel):
    phone: str = Field(..., example="+79123456789")

class SMSVerification(BaseModel):
    phone: str = Field(..., example="+79123456789")
    code: str = Field(..., min_length=4, max_length=6, example="1234")

class UserCreate(BaseModel):
    phone: str = Field(..., example="+79123456789")
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Иван Иванов")
    age: Optional[int] = Field(None, ge=0, le=120, example=30)
    weight: Optional[float] = Field(None, gt=0, example=70.5)
    height: Optional[float] = Field(None, gt=0, example=175.0)
    gender: Optional[str] = Field(None, example="мужской")
    activity_level: Optional[str] = Field(None, example="умеренная")
    allergies: Optional[str] = Field(None, example="лактоза, арахис")

class User(BaseModel):
    id: int
    phone: str
    name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    allergies: Optional[str] = None

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    user: User
    access_token: str
    token_type: str

class Token(BaseModel):
    access_token: str
    token_type: str