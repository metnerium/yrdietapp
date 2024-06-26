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
    pass

class RecipeResponse(RecipeBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True