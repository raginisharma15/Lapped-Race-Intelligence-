import pandas as pd
from sklearn.linear_model import LinearRegression

from app.utils.schemas import TireDegradationReport
from config import get_settings


def build_tire_degradation_report(
    df: pd.DataFrame, threshold_seconds: float | None = None
) -> list[TireDegradationReport]:
    """Fit per-compound degradation model and estimate pit window."""
    settings = get_settings()
    cliff_threshold = threshold_seconds if threshold_seconds is not None else max(0.1, settings.anomaly_threshold * 5)
    if df.empty or "tyre_compound" not in df.columns:
        return []

    reports: list[TireDegradationReport] = []
    for compound, chunk in df.dropna(subset=["tyre_compound"]).groupby("tyre_compound"):
        if len(chunk) < 3 or "tyre_age" not in chunk.columns or "lap_time" not in chunk.columns:
            continue
        work = chunk[["tyre_age", "lap_time", "lap_number"]].dropna()
        if len(work) < 3:
            continue
        model = LinearRegression()
        model.fit(work[["tyre_age"]], work["lap_time"])
        deg_rate = float(model.coef_[0])
        laps_to_cliff = int(max(1, cliff_threshold / max(0.001, deg_rate)))
        recommended_pit_lap = int(work["lap_number"].max() + laps_to_cliff)
        reports.append(
            TireDegradationReport(
                compound=str(compound),
                deg_rate=deg_rate,
                laps_to_cliff=laps_to_cliff,
                recommended_pit_lap=recommended_pit_lap,
            )
        )
    return reports
