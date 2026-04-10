from fastapi import APIRouter

from app.ml.anomaly_detector import run_anomaly_detection
from app.ml.engine_monitor import analyze_engine_health
from app.ml.overtake_analyzer import analyze_overtakes
from app.ml.sector_analyzer import analyze_sectors
from app.ml.tire_model import build_tire_degradation_report
from app.services.pipeline import get_session_dataframe

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/{session_key}/anomalies")
async def anomalies(session_key: str) -> list[dict]:
    """Return anomaly results."""
    df = await get_session_dataframe(session_key)
    return [item.model_dump() for item in run_anomaly_detection(df)]


@router.get("/{session_key}/tires")
async def tires(session_key: str) -> list[dict]:
    """Return tire degradation report."""
    df = await get_session_dataframe(session_key)
    return [item.model_dump() for item in build_tire_degradation_report(df)]


@router.get("/{session_key}/engine")
async def engine(session_key: str) -> list[dict]:
    """Return engine health flags."""
    df = await get_session_dataframe(session_key)
    return [item.model_dump() for item in analyze_engine_health(df)]


@router.get("/{session_key}/sectors")
async def sectors(session_key: str) -> list[dict]:
    """Return sector analysis report."""
    df = await get_session_dataframe(session_key)
    return [item.model_dump() for item in analyze_sectors(df)]


@router.get("/{session_key}/overtakes")
async def overtakes(session_key: str) -> list[dict]:
    """Return overtake events."""
    df = await get_session_dataframe(session_key)
    return [item.model_dump() for item in analyze_overtakes(df)]
