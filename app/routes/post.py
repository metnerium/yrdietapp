from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.dependencies import get_current_user_dependency
from typing import List

router = APIRouter()

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, current_user: User = Depends(get_current_user_dependency), db: AsyncSession = Depends(get_db)):
    db_post = Post(**post.model_dump(), user_id=current_user.id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return PostResponse(user_nickname=current_user.nickname, **db_post.__dict__)

@router.get("/{post_id}", response_model=PostResponse)
async def read_post(post_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Post).options(joinedload(Post.user)).filter(Post.id == post_id)
    result = await db.execute(query)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse(user_nickname=post.user.nickname, **post.__dict__)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostUpdate, current_user: User = Depends(get_current_user_dependency),
                      db: AsyncSession = Depends(get_db)):
    db_post = await db.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")

    update_data = post.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)

    await db.commit()
    await db.refresh(db_post)
    return PostResponse(user_nickname=current_user.nickname, **db_post.__dict__)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, current_user: User = Depends(get_current_user_dependency),
                      db: AsyncSession = Depends(get_db)):
    db_post = await db.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    await db.delete(db_post)
    await db.commit()

@router.get("/", response_model=List[PostResponse])
async def list_posts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(Post).options(joinedload(Post.user)).offset(skip).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()
    return [PostResponse(user_nickname=post.user.nickname, **post.__dict__) for post in posts]