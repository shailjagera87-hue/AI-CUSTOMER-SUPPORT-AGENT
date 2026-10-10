
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.session import initialize_database


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    yield

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "AI Customer Support Agent API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
