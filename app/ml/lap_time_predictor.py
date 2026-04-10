import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from config import get_settings


def run_lap_time_prediction(df: pd.DataFrame) -> list[dict[str, float | int | bool]]:
    """Predict expected lap time and flag underperformance per driver."""
    settings = get_settings()
    if df.empty:
        return []

    work = df.copy()
    work["tyre_compound_enc"] = work.get("tyre_compound", "UNKNOWN").astype("category").cat.codes
    work["fuel_load_est"] = work.groupby("driver_number")["lap_number"].transform(lambda s: s.max() - s)
    if "air_temp" not in work.columns:
        work["air_temp"] = 0.0
    if "track_temp" not in work.columns:
        work["track_temp"] = 0.0

    feature_cols = [
        "tyre_compound_enc",
        "tyre_age",
        "fuel_load_est",
        "air_temp",
        "track_temp",
        "sector_1",
        "sector_2",
    ]
    target_col = "lap_time"
    for col in feature_cols + [target_col]:
        if col not in work.columns:
            work[col] = 0.0
    work = work.dropna(subset=["driver_number", "lap_number"])
    work[feature_cols + [target_col]] = work[feature_cols + [target_col]].fillna(0.0)

    outputs: list[dict[str, float | int | bool]] = []
    for driver, chunk in work.groupby("driver_number"):
        if len(chunk) < 5:
            continue
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(chunk[feature_cols], chunk[target_col])
        preds = model.predict(chunk[feature_cols])
        for i, (_, row) in enumerate(chunk.iterrows()):
            actual = float(row[target_col])
            predicted = float(preds[i])
            delta = actual - predicted
            outputs.append(
                {
                    "driver_number": int(driver),
                    "lap_number": int(row["lap_number"]),
                    "actual_lap_time": actual,
                    "predicted_lap_time": predicted,
                    "performance_delta": delta,
                    "underperformed": bool(delta > settings.anomaly_threshold),
                }
            )
    return outputs
