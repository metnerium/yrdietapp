# app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.admin import Admin
from app.models.user import User
from app.models.post import Post
from app.models.recipes import Recipe
from app.schemas.admin import AdminCreate, AdminUpdate, AdminInDB, AdminResponse
from app.schemas.user import UserInDB
from app.schemas.post import PostResponse
from app.schemas.recipes import RecipeResponse
from app.utils.security import create_access_token, verify_password, get_password_hash
from app.dependencies import get_current_admin
from typing import List

router = APIRouter()

@router.post("/login", response_model=AdminResponse)
async def login_admin(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    admin = await Admin.get_by_username(db, form_data.username)
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": admin.username, "is_admin": True})
    return AdminResponse(admin=AdminInDB.from_orm(admin), access_token=access_token, token_type="bearer")

@router.post("/create", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
async def create_admin(admin: AdminCreate, db: AsyncSession = Depends(get_db),
                       current_admin: Admin = Depends(get_current_admin)):
    if not current_admin.is_superadmin:
        raise HTTPException(status_code=403, detail="Only superadmins can create new admins")

    existing_admin = await Admin.get_by_username(db, admin.username)
    if existing_admin:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_admin = await Admin.create_admin(db, admin.username, admin.password, admin.is_superadmin)
    access_token = create_access_token(data={"sub": new_admin.username, "is_admin": True})
    return AdminResponse(admin=AdminInDB.from_orm(new_admin), access_token=access_token, token_type="bearer")


@router.get("/me", response_model=AdminInDB)
async def read_admin_me(current_admin: Admin = Depends(get_current_admin)):
    return current_admin


@router.patch("/me", response_model=AdminInDB)
async def update_admin_me(admin_update: AdminUpdate, current_admin: Admin = Depends(get_current_admin),
                          db: AsyncSession = Depends(get_db)):
    if admin_update.password:
        current_admin.hashed_password = get_password_hash(admin_update.password)
    if admin_update.is_superadmin is not None and current_admin.is_superadmin:
        current_admin.is_superadmin = admin_update.is_superadmin

    db.add(current_admin)
    await db.commit()
    await db.refresh(current_admin)
    return current_admin


@router.get("/users", response_model=List[UserInDB])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                     current_admin: Admin = Depends(get_current_admin)):
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=UserInDB)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}/block", response_model=UserInDB)
async def block_unblock_user(user_id: int, block: bool, db: AsyncSession = Depends(get_db),
                             current_admin: Admin = Depends(get_current_admin)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_blocked = block
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db),
                      current_admin: Admin = Depends(get_current_admin)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()


@router.get("/posts", response_model=List[PostResponse])
async def list_posts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                     current_admin: Admin = Depends(get_current_admin)):
    query = select(Post).options(joinedload(Post.user)).offset(skip).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()
    return [PostResponse(user_nickname=post.user.nickname, **post.__dict__) for post in posts]


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db),
                      current_admin: Admin = Depends(get_current_admin)):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(post)
    await db.commit()


@router.get("/recipes", response_model=List[RecipeResponse])
async def list_recipes(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                       current_admin: Admin = Depends(get_current_admin)):
    query = select(Recipe).options(joinedload(Recipe.user)).offset(skip).limit(limit)
    result = await db.execute(query)
    recipes = result.scalars().all()
    return [RecipeResponse(user_nickname=recipe.user.nickname, **recipe.__dict__) for recipe in recipes]


@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: int, db: AsyncSession = Depends(get_db),
                        current_admin: Admin = Depends(get_current_admin)):
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    await db.delete(recipe)
    await db.commit()


@router.get("/statistics", response_model=dict)
async def get_statistics(db: AsyncSession = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    user_count = await db.execute(select(func.count(User.id)))
    post_count = await db.execute(select(func.count(Post.id)))
    recipe_count = await db.execute(select(func.count(Recipe.id)))

    return {
        "total_users": user_count.scalar(),
        "total_posts": post_count.scalar(),
        "total_recipes": recipe_count.scalar()
    }


@router.post("/send-notification", status_code=status.HTTP_200_OK)
async def send_notification(user_id: int, message: str, db: AsyncSession = Depends(get_db),
                            current_admin: Admin = Depends(get_current_admin)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Here you would implement the logic to send a notification to the user
    # For example, you might use a third-party service or send an email

    return {"status": "Notification sent successfully"}


@router.get("/audit-log", response_model=List[dict])
async def get_audit_log(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                        current_admin: Admin = Depends(get_current_admin)):
    # Implement audit log retrieval logic here
    # This could involve querying a separate audit log table

    return [{"action": "user_created", "timestamp": "2023-05-01T12:00:00Z"}]  # Placeholder