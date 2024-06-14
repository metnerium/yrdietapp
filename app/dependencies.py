from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.security import get_current_user
from app.utils.exceptions import CREDENTIALS_EXCEPTION, USER_NOT_FOUND_EXCEPTION
from app.models.user import User
from app.database import get_db

async def get_current_user_dependency(token: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        user = await User.get_by_phone(db, token)
        if not user:
            raise USER_NOT_FOUND_EXCEPTION
        return user
    except:
        raise CREDENTIALS_EXCEPTION