from pydantic import BaseModel
from typing import Optional

class RecipeBase(BaseModel):
    name: str
    description: str
    image_url: str
    ingredients: str
    cost: float
    calories: float
    protein: float
    fat: float
    carbohydrates: float
    category: str
    cooking_time: int
    instructions: str

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(RecipeBase):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    ingredients: Optional[str] = None
    cost: Optional[float] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbohydrates: Optional[float] = None
    category: Optional[str] = None
    cooking_time: Optional[int] = None
    instructions: Optional[str] = None

class RecipeResponse(RecipeBase):
    id: int
    user_id: int
    user_nickname: str  # Added user_nickname field

    class Config:
        from_attributes = True