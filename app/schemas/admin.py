from pydantic import BaseModel, Field

class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    is_superadmin: bool = False

class AdminUpdate(BaseModel):
    password: str = Field(None, min_length=8)
    is_superadmin: bool = None

class AdminInDB(BaseModel):
    id: int
    username: str
    is_superadmin: bool

    class Config:
        from_attributes = True

class AdminResponse(BaseModel):
    admin: AdminInDB
    access_token: str
    token_type: str