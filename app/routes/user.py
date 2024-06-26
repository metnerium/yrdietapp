from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.sms_code import SMSCode
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema, UserResponse
from app.utils.security import get_password_hash, create_access_token
from app.dependencies import get_current_user_dependency

router = APIRouter()


@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, был ли подтвержден номер телефона
    sms_code = await db.execute(select(SMSCode).where(SMSCode.phone == user.phone, SMSCode.is_verified == True))
    sms_code = sms_code.scalar_one_or_none()

    if not sms_code:
        raise HTTPException(status_code=400, detail="Номер телефона не подтвержден")

    # Проверяем, не существует ли уже пользователь с таким номером телефона
    existing_user = await db.execute(select(User).where(User.phone == user.phone))
    existing_user = existing_user.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким номером телефона уже существует")

    # Создаем пользователя
    hashed_password = get_password_hash(user.password)
    db_user = User(**user.dict(exclude={"password"}), hashed_password=hashed_password)
    db.add(db_user)

    # Удаляем запись о коде подтверждения
    await db.delete(sms_code)

    await db.commit()
    await db.refresh(db_user)

    # Генерируем JWT
    access_token = create_access_token(data={"sub": db_user.phone})

    return UserResponse(
        user=db_user,
        access_token=access_token,
        token_type="bearer"
    )
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