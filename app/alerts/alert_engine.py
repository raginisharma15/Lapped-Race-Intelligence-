from collections import deque
from datetime import datetime, timezone

import pandas as pd

from app.utils.schemas import EngineFlag, OvertakeEvent, RaceAlert, TireDegradationReport
from config import get_settings


class AlertEngine:
    """Generate and store race alerts in bounded memory."""

    def __init__(self) -> None:
        settings = get_settings()
        self.buffer: deque[RaceAlert] = deque(maxlen=settings.alert_buffer_size)

    def _push(self, alert: RaceAlert) -> None:
        self.buffer.append(alert)

    def generate_alerts(
        self,
        df: pd.DataFrame,
        tire_reports: list[TireDegradationReport],
        engine_flags: list[EngineFlag],
        overtake_events: list[OvertakeEvent],
    ) -> list[RaceAlert]:
        """Generate alerts from analysis outputs."""
        now = datetime.now(timezone.utc)

        for report in tire_reports:
            if report.deg_rate > 0.4 and report.laps_to_cliff <= 15:
                self._push(
                    RaceAlert(
                        severity="CRITICAL",
                        category="TIRE_DEGRADATION",
                        driver=None,
                        message=f"{report.compound} degradation critical ({report.deg_rate:.2f}s/lap).",
                        timestamp=now,
                    )
                )

        for flag in engine_flags:
            if flag.overheating_risk:
                self._push(
                    RaceAlert(
                        severity="WARNING",
                        category="ENGINE_TEMP",
                        driver=flag.driver_number,
                        message="RPM anomaly sustained for 3 laps.",
                        timestamp=now,
                    )
                )

        for event in overtake_events:
            self._push(
                RaceAlert(
                    severity="INFO",
                    category="POSITION_CHANGE",
                    driver=event.driver,
                    message=f"Position change on lap {event.lap} in {event.zone}.",
                    timestamp=now,
                )
            )

        if not df.empty and "lap_time" in df.columns:
            median = float(df["lap_time"].median())
            std = float(df["lap_time"].std() or 0.0)
            threshold = median + (3 * std)
            bad = df[df["lap_time"] > threshold]
            for _, row in bad.iterrows():
                self._push(
                    RaceAlert(
                        severity="CRITICAL",
                        category="LAP_TIME_ANOMALY",
                        driver=int(row["driver_number"]) if pd.notna(row["driver_number"]) else None,
                        message=f"Lap {int(row['lap_number'])} exceeds anomaly threshold.",
                        timestamp=now,
                    )
                )

        return list(self.buffer)

    def get_alerts(self, severity: str | None = None) -> list[RaceAlert]:
        """Return all alerts or filter by severity."""
        alerts = list(self.buffer)
        if severity is None:
            return sorted(alerts, key=lambda a: a.severity)
        return [a for a in alerts if a.severity == severity]
