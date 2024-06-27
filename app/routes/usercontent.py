from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.recipes import Recipe
from app.models.post import Post
from app.schemas.recipes import RecipeResponse
from app.schemas.post import PostResponse
from app.dependencies import get_current_user_dependency
from app.models.user import User
from typing import List

router = APIRouter()

@router.get("/my-recipes", response_model=List[RecipeResponse])
async def get_my_recipes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    query = select(Recipe).filter(Recipe.user_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(query)
    recipes = result.scalars().all()
    return [RecipeResponse.model_validate(recipe.__dict__) for recipe in recipes]

@router.get("/my-posts", response_model=List[PostResponse])
async def get_my_posts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    query = select(Post).filter(Post.user_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()
    return [PostResponse.model_validate(post.__dict__) for post in posts]