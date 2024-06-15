from fastapi import APIRouter
import pandas as pd
from fastapi.params import Body

router = APIRouter()

@router.post("/search_recipes_by_ingredients")
async def search_recipes_by_ingredients(ingredients_list: list[str]):
    data = pd.read_csv('./res/recipes.csv')
    data['ingredients'] = data['ingredients'].fillna('')
    ingredients_list_lower = [ingredient.lower() for ingredient in ingredients_list]
    # Фильтрация данных по столбцу "ingredients"
    filtered_data = data[data['ingredients'].apply(lambda x: all(ingredient.lower() in x.lower() for ingredient in ingredients_list_lower))]
    # Ограничение списка до 5 рецептов
    filtered_data = filtered_data.head(100)
    # Возвращение найденных рецептов в виде JSON
    recipes = []
    for _, row in filtered_data.iterrows():
        recipe = {
            "url": row['url'],
            "name": row['name'],
        }
        recipes.append(recipe)
    return {"recipes": recipes}

@router.post("/search_recipes_by_name")
async def search_recipes_by_name(data: dict = Body(...)):
    recipe_name = data.get("recipe_name", "")
    data = pd.read_csv('./res/recipes.csv')
    # Фильтрация данных по столбцу "name"
    filtered_data = data[data['name'].str.contains(recipe_name, case=False)]
    # Ограничение списка до 1000 рецептов
    filtered_data = filtered_data.head(100)
    # Возвращение найденных рецептов в виде JSON
    recipes = []
    for _, row in filtered_data.iterrows():
        recipe = {
            "url": row['url'],
            "name": row['name'],
        }
        recipes.append(recipe)
    return {"recipes": recipes}