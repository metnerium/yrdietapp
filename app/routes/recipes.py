from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.recipes import Recipe
from app.schemas.recipes import RecipeCreate, RecipeUpdate, RecipeResponse
from app.dependencies import get_current_user_dependency
from app.models.user import User
from typing import List

router = APIRouter()


@router.get("/search", response_model=List[RecipeResponse])
async def search_recipes(name: str = None, ingredients: str = None, db: AsyncSession = Depends(get_db)):
    query = select(Recipe)
    if name:
        query = query.filter(Recipe.name.ilike(f"%{name}%"))
    if ingredients:
        ingredient_list = [ing.strip() for ing in ingredients.split(',')]
        for ingredient in ingredient_list:
            query = query.filter(Recipe.ingredients.ilike(f"%{ingredient}%"))
    result = await db.execute(query)
    recipes = result.scalars().all()
    return recipes


@router.get("/categories", response_model=List[str])
async def get_recipe_categories(db: AsyncSession = Depends(get_db)):
    query = select(Recipe.category).distinct()
    result = await db.execute(query)
    categories = result.scalars().all()
    return categories


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe: RecipeCreate, current_user: User = Depends(get_current_user_dependency),
                        db: AsyncSession = Depends(get_db)):
    db_recipe = Recipe(**recipe.dict(), user_id=current_user.id)
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def read_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(recipe_id: int, recipe: RecipeUpdate, current_user: User = Depends(get_current_user_dependency),
                        db: AsyncSession = Depends(get_db)):
    db_recipe = await db.get(Recipe, recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if db_recipe.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this recipe")

    for key, value in recipe.dict(exclude_unset=True).items():
        setattr(db_recipe, key, value)

    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: int, current_user: User = Depends(get_current_user_dependency),
                        db: AsyncSession = Depends(get_db)):
    db_recipe = await db.get(Recipe, recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if db_recipe.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this recipe")

    await db.delete(db_recipe)
    await db.commit()


@router.get("/", response_model=List[RecipeResponse])
async def list_recipes(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(Recipe).offset(skip).limit(limit)
    result = await db.execute(query)
    recipes = result.scalars()