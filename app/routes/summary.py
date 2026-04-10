from fastapi import APIRouter

from app.ai.summariser import generate_race_summary
from app.alerts.alert_engine import AlertEngine
from app.ml.anomaly_detector import run_anomaly_detection
from app.ml.engine_monitor import analyze_engine_health
from app.ml.overtake_analyzer import analyze_overtakes
from app.ml.sector_analyzer import analyze_sectors
from app.ml.tire_model import build_tire_degradation_report
from app.services.pipeline import get_session_dataframe

router = APIRouter(prefix="/summary", tags=["summary"])
alert_engine = AlertEngine()


async def _build_analysis_payload(session_key: str) -> dict:
    df = await get_session_dataframe(session_key)
    anomalies = [item.model_dump() for item in run_anomaly_detection(df)]
    tires = [item.model_dump() for item in build_tire_degradation_report(df)]
    engine = [item.model_dump() for item in analyze_engine_health(df)]
    sectors = [item.model_dump() for item in analyze_sectors(df)]
    overtakes = [item.model_dump() for item in analyze_overtakes(df)]
    alerts = [
        item.model_dump()
        for item in alert_engine.generate_alerts(
            df,
            build_tire_degradation_report(df),
            analyze_engine_health(df),
            analyze_overtakes(df),
        )
    ]
    return {
        "session_key": session_key,
        "anomalies": anomalies,
        "tire_degradation_report": tires,
        "engine_warnings": engine,
        "sector_time_losses": sectors,
        "overtake_events": overtakes,
        "alerts": alerts,
    }


@router.get("/{session_key}")
async def get_summary(session_key: str) -> dict:
    """Return AI generated race summary."""
    payload = await _build_analysis_payload(session_key)
    summary = await generate_race_summary(payload)
    return summary.model_dump()


@router.post("/{session_key}/refresh")
async def refresh_summary(session_key: str) -> dict:
    """Force rerun all analysis modules and regenerate summary."""
    payload = await _build_analysis_payload(session_key)
    summary = await generate_race_summary(payload)
    return summary.model_dump()
