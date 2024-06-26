from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.schemas.auth import PhoneNumber, SMSVerification
from app.schemas.user import UserCreate, UserResponse
from app.utils.security import create_access_token, get_password_hash, verify_password
from app.utils.sms import get_auth_code, send_sms
from app.utils.phone import normalize_phone_number

router = APIRouter()


@router.post("/request-sms")
async def request_sms(phone_data: PhoneNumber, db: AsyncSession = Depends(get_db)):
    normalized_phone = normalize_phone_number(phone_data.phone)
    user = await User.get_by_phone(db, normalized_phone)

    code = get_auth_code()

    if user:
        user.sms_code = code
        user.is_phone_verified = False
    else:
        new_user = User(
            phone=normalized_phone,
            sms_code=code,
            is_phone_verified=False
        )
        db.add(new_user)

    await db.commit()

    if send_sms(normalized_phone, code):
        return {"message": "SMS успешно отправлено"}
    else:
        raise HTTPException(status_code=500, detail="Не удалось отправить SMS")


@router.post("/verify-sms")
async def verify_sms(verification: SMSVerification, db: AsyncSession = Depends(get_db)):
    normalized_phone = normalize_phone_number(verification.phone)
    user = await User.get_by_phone(db, normalized_phone)

    if not user or user.sms_code != verification.code:
        raise HTTPException(status_code=400, detail="Неверный код")

    user.is_phone_verified = True
    user.sms_code = None
    await db.commit()

    return {"message": "Номер телефона подтвержден"}


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    normalized_phone = normalize_phone_number(user.phone)
    db_user = await User.get_by_phone(db, normalized_phone)

    if not db_user:
        raise HTTPException(status_code=400, detail="Номер телефона не найден. Пожалуйста, запросите SMS-код")

    if not db_user.is_phone_verified:
        raise HTTPException(status_code=400, detail="Номер телефона не подтвержден")

    if db_user.hashed_password:
        raise HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")

    hashed_password = get_password_hash(user.password)
    db_user.hashed_password = hashed_password
    await db.commit()
    await db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.phone})

    return UserResponse(
        user=db_user,
        access_token=access_token,
        token_type="bearer"
    )


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    normalized_phone = normalize_phone_number(form_data.username)
    user = await User.get_by_phone(db, normalized_phone)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный номер телефона или пароль")
    access_token = create_access_token(data={"sub": user.phone})
    return {"access_token": access_token, "token_type": "bearer"}