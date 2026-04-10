from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes.alerts import router as alerts_router
from app.routes.analysis import router as analysis_router
from app.routes.summary import router as summary_router
from app.routes.telemetry import router as telemetry_router
from app.services.pipeline import get_session_dataframe
from config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Warm up data pipeline at startup."""
    await get_session_dataframe(settings.default_session_key)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, World!"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Return structured JSON for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={"error": {"type": exc.__class__.__name__, "message": str(exc)}},
    )


app.include_router(telemetry_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(summary_router, prefix="/api/v1")
