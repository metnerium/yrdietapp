from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, User as UserSchema
from app.dependencies import get_current_user_dependency

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_user_me(current_user: User = Depends(get_current_user_dependency)):
    return current_user


@router.patch("/me", response_model=UserSchema)
async def update_user_me(user_update: UserUpdate, current_user: User = Depends(get_current_user_dependency),
                         db: AsyncSession = Depends(get_db)):
    if user_update.nickname and user_update.nickname != current_user.nickname:
        existing_user = await User.get_by_nickname(db, user_update.nickname)
        if existing_user:
            raise HTTPException(status_code=400, detail="Этот никнейм уже занят")

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(current_user: User = Depends(get_current_user_dependency), db: AsyncSession = Depends(get_db)):
    await db.delete(current_user)
    await db.commit()