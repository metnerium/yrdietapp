import logging
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.admin import oauth2_scheme
from app.models.admin import Admin
from app.utils.security import get_current_user, decode_access_token
from app.utils.exceptions import CREDENTIALS_EXCEPTION, USER_NOT_FOUND_EXCEPTION
from app.models.user import User
from app.database import get_db

logger = logging.getLogger(__name__)

async def get_current_user_dependency(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Attempting to get user with ID: {current_user.id}")
        user = await User.get_by_phone(db, current_user.phone)
        if not user:
            logger.error(f"User not found for phone: {current_user.phone}")
            raise USER_NOT_FOUND_EXCEPTION
        logger.info(f"User found: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Error in get_current_user_dependency: {str(e)}")
        raise CREDENTIALS_EXCEPTION


async def get_current_admin(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if not is_admin:
            raise HTTPException(status_code=403, detail="Not an admin")

        admin = await Admin.get_by_username(db, username)
        if not admin:
            raise HTTPException(status_code=403, detail="Admin not found")

        return admin
    except Exception as e:
        logger.error(f"Error in get_current_admin: {str(e)}")
        raise HTTPException(status_code=403, detail="Could not validate admin credentials")