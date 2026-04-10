import pandas as pd
from sklearn.ensemble import IsolationForest

from app.utils.schemas import AnomalyResult
from config import get_settings


def run_anomaly_detection(df: pd.DataFrame) -> list[AnomalyResult]:
    """Detect per-lap anomalies using Isolation Forest."""
    settings = get_settings()
    if df.empty:
        return []
    features = ["lap_time", "sector_1", "sector_2", "sector_3", "engine_rpm", "throttle_pct"]
    work = df.dropna(subset=["driver_number", "lap_number"]).copy()
    for feature in features:
        if feature not in work.columns:
            work[feature] = 0.0
    work[features] = work[features].fillna(work[features].median(numeric_only=True)).fillna(0.0)

    contamination = min(max(settings.anomaly_threshold, 0.01), 0.4)
    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(work[features])
    scores = model.decision_function(work[features])
    preds = model.predict(work[features])
    center = work[features].median(numeric_only=True)

    results: list[AnomalyResult] = []
    for pos, (_, row) in enumerate(work.iterrows()):
        deviations = (row[features] - center).abs()
        most_feature = str(deviations.idxmax())
        results.append(
            AnomalyResult(
                driver_number=int(row["driver_number"]),
                lap_number=int(row["lap_number"]),
                anomaly_score=float(scores[pos]),
                is_anomaly=bool(preds[pos] == -1),
                most_anomalous_feature=most_feature,
            )
        )
    return results
