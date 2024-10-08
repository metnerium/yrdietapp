import asyncio
import uvicorn
from fastapi import FastAPI

from app.database import create_tables
from app.routes import user, auth, recipes, post, dailycalory, gpt, usercontent, admin
from app.middleware.admin import admin_middleware
app = FastAPI()
app.include_router(user.router, prefix="/users", tags=["users"])

app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(auth.router,  tags=["auth"])
app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(post.router, prefix="/posts", tags=["blog"])
app.include_router(dailycalory.router, prefix="/app", tags=["app"])
app.include_router(gpt.router, prefix="/gpt", tags=["app"])

app.include_router(usercontent.router, prefix="/app", tags=["app"])
admin_router = FastAPI()
admin_router.include_router(admin.router, prefix="/admin", tags=["admin"])
app.mount("/admin", admin_router)
admin_router.middleware("http")(admin_middleware)
@app.on_event("startup")
async def startup_event():
    await create_tables()

@app.on_event("shutdown")
async def shutdown_event():
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)