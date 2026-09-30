from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .api.v1.router import router
from .core.config import settings
from .db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tests use an isolated SQLite database; production schema changes are managed by Alembic.
    if settings.app_env == "test":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="CV Guard & Recruit API", version="1.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "degraded", "database": "unavailable"})


app.include_router(router, prefix="/api/v1")


@app.exception_handler(Exception)
async def unhandled_exception(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
