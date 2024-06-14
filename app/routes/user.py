from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.utils.security import get_password_hash
from app.dependencies import get_current_user_dependency

router = APIRouter()

@router.post("/create", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await User.get_by_phone(db, user.phone)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(**user.dict(exclude={"password"}), hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserSchema)
async def read_user_me(current_user: User = Depends(get_current_user_dependency)):
    return current_user

@router.patch("/me", response_model=UserSchema)
async def update_user_me(user_update: UserUpdate, current_user: User = Depends(get_current_user_dependency), db: AsyncSession = Depends(get_db)):
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