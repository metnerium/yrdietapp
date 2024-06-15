import asyncio
import uvicorn
from fastapi import FastAPI

from app.database import create_tables
from app.routes import user, auth, recipes, post, dailycalory

app = FastAPI()

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(auth.router,  tags=["auth"])
app.include_router(recipes.router, prefix="/app", tags=["app"])
app.include_router(post.router, prefix="/posts", tags=["blog"])
app.include_router(dailycalory.router, prefix="/app", tags=["app"])
@app.on_event("startup")
async def startup_event():
    await create_tables()

@app.on_event("shutdown")
async def shutdown_event():
    pass
