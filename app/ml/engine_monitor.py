import pandas as pd

from app.utils.schemas import EngineFlag


def analyze_engine_health(df: pd.DataFrame) -> list[EngineFlag]:
    """Detect overheating risk and mapping changes from RPM behavior."""
    if df.empty:
        return []
    if "engine_rpm" not in df.columns:
        return []

    flags: list[EngineFlag] = []
    for driver, chunk in df.groupby("driver_number"):
        work = chunk.sort_values("lap_number").copy()
        rpm = work["engine_rpm"].fillna(0)
        pct95 = rpm.quantile(0.95)
        hot = rpm > pct95
        consecutive = (hot.rolling(3).sum() >= 3).any()

        rolling_mean = rpm.rolling(window=3, min_periods=2).mean()
        rolling_std = rpm.rolling(window=3, min_periods=2).std().replace(0, 1)
        z = (rpm - rolling_mean) / rolling_std
        mapping_change = (z < -2.0).any()

        flags.append(
            EngineFlag(
                driver_number=int(driver),
                overheating_risk=bool(consecutive),
                mapping_change_detected=bool(mapping_change),
            )
        )
    return flags
