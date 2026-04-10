from fastapi import APIRouter

from app.alerts.alert_engine import AlertEngine
from app.ml.engine_monitor import analyze_engine_health
from app.ml.overtake_analyzer import analyze_overtakes
from app.ml.tire_model import build_tire_degradation_report
from app.services.pipeline import get_session_dataframe

router = APIRouter(prefix="/alerts", tags=["alerts"])
alert_engine = AlertEngine()


@router.get("/{session_key}")
async def all_alerts(session_key: str) -> list[dict]:
    """Return all alerts sorted by severity."""
    df = await get_session_dataframe(session_key)
    tire = build_tire_degradation_report(df)
    engine = analyze_engine_health(df)
    overtakes = analyze_overtakes(df)
    alerts = alert_engine.generate_alerts(df, tire, engine, overtakes)
    return [item.model_dump() for item in alerts]


@router.get("/{session_key}/critical")
async def critical_alerts(session_key: str) -> list[dict]:
    """Return only critical alerts."""
    await all_alerts(session_key)
    return [item.model_dump() for item in alert_engine.get_alerts("CRITICAL")]
