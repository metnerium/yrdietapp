# app/middleware/admin.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.utils.security import decode_access_token
from app.models.admin import Admin
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def admin_middleware(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if not is_admin:
            raise HTTPException(status_code=403, detail="Not an admin")

        db = next(get_db())
        admin = await Admin.get_by_username(db, username)
        if not admin:
            raise HTTPException(status_code=403, detail="Admin not found")

        request.state.admin = admin
    except Exception:
        raise HTTPException(status_code=403, detail="Could not validate admin credentials")