import pytz
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.sms_code import SMSCode
from app.schemas.auth import PhoneNumber, SMSVerification
from app.utils.security import create_access_token
from app.utils.sms import get_auth_code, send_sms
from datetime import datetime, timedelta, UTC

router = APIRouter()


@router.post("/request-sms")
async def request_sms(phone_data: PhoneNumber, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.phone == phone_data.phone))
    user = user.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="Номер телефона уже зарегистрирован")

    code = get_auth_code()

    # Проверяем, есть ли уже код для этого номера
    existing_code = await db.execute(select(SMSCode).where(SMSCode.phone == phone_data.phone))
    existing_code = existing_code.scalar_one_or_none()

    if existing_code:
        existing_code.code = code
        existing_code.created_at = datetime.now(pytz.UTC)
    else:
        new_code = SMSCode(phone=phone_data.phone, code=code)
        db.add(new_code)

    await db.commit()

    if send_sms(phone_data.phone, code):
        return {"message": "SMS успешно отправлено"}
    else:
        raise HTTPException(status_code=500, detail="Не удалось отправить SMS")


@router.post("/verify-sms")
async def verify_sms(verification: SMSVerification, db: AsyncSession = Depends(get_db)):
    sms_code = await db.execute(select(SMSCode).where(SMSCode.phone == verification.phone))
    sms_code = sms_code.scalar_one_or_none()

    if not sms_code or sms_code.code != verification.code:
        raise HTTPException(status_code=400, detail="Неверный код")

    # Проверяем, не истек ли срок действия кода (например, 15 минут)
    if datetime.now(pytz.UTC) - sms_code.created_at.replace(tzinfo=pytz.UTC) > timedelta(minutes=15):
        await db.delete(sms_code)
        await db.commit()
        raise HTTPException(status_code=400, detail="Срок действия кода истек")

    # Код верный, обновляем статус подтверждения
    sms_code.is_verified = True
    await db.commit()

    return {"message": "Код подтвержден"}
# Update the existing login endpoint to use phone instead of username
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await User.get_by_phone(db, form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone number")
    access_token = create_access_token(data={"sub": user.phone})
    return {"access_token": access_token, "token_type": "bearer"}