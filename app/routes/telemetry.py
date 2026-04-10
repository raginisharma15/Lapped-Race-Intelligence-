from fastapi import APIRouter

from app.services.pipeline import get_session_dataframe

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.get("/{session_key}/laps")
async def get_session_laps(session_key: str) -> list[dict]:
    """Return unified session telemetry as JSON rows."""
    df = await get_session_dataframe(session_key)
    return df.fillna("").to_dict(orient="records")


@router.get("/{session_key}/driver/{driver_number}")
async def get_driver_laps(session_key: str, driver_number: int) -> list[dict]:
    """Return per-driver telemetry rows."""
    df = await get_session_dataframe(session_key)
    filtered = df[df["driver_number"] == driver_number]
    return filtered.fillna("").to_dict(orient="records")
