import pandas as pd

from app.utils.schemas import OvertakeEvent


def analyze_overtakes(df: pd.DataFrame) -> list[OvertakeEvent]:
    """Identify laps with position gain and score likely overtake zones."""
    if df.empty or "position" not in df.columns:
        return []

    events: list[OvertakeEvent] = []
    for driver, chunk in df.sort_values("lap_number").groupby("driver_number"):
        work = chunk.copy()
        work["prev_pos"] = work["position"].shift(1)
        work["gain"] = work["prev_pos"] - work["position"]
        candidates = work[work["gain"] > 0]
        for _, row in candidates.iterrows():
            zone = "Sector 2 DRS Zone"
            speed_delta = float(row.get("speed_trap", 0.0) - work["speed_trap"].median())
            events.append(
                OvertakeEvent(
                    lap=int(row["lap_number"]),
                    driver=int(driver),
                    position_gained=int(row["gain"]),
                    zone=zone,
                    speed_delta=speed_delta,
                )
            )
    return events
