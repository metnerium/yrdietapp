from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None

class PostResponse(PostBase):
    id: int
    user_id: int
    user_nickname: str  # Added user_nickname field
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True  # For Pydantic v1
        from_attributes = True  # For Pydantic v2