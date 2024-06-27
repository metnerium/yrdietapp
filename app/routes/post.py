from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.dependencies import get_current_user_dependency
from app.models.user import User
from typing import List

router = APIRouter()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, current_user: User = Depends(get_current_user_dependency), db: AsyncSession = Depends(get_db)):
    db_post = Post(**post.dict(), user_id=current_user.id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return PostResponse.from_orm(db_post)

@router.get("/{post_id}", response_model=PostResponse)
async def read_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse.from_orm(post)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostUpdate, current_user: User = Depends(get_current_user_dependency),
                      db: AsyncSession = Depends(get_db)):
    db_post = await db.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")

    update_data = post.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)

    await db.commit()
    await db.refresh(db_post)
    return PostResponse.from_orm(db_post)


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
    query = select(Post).offset(skip).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()
    return [PostResponse.from_orm(post) for post in posts]