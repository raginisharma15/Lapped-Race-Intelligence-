from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class LapRecord(BaseModel):
    driver_number: int | None = None
    lap_number: int | None = None
    lap_time: float | None = None
    sector_1: float | None = None
    sector_2: float | None = None
    sector_3: float | None = None


class CarDataRecord(BaseModel):
    driver_number: int | None = None
    rpm: float | None = None
    throttle: float | None = None
    brake: float | None = None
    drs: int | None = None
    n_gear: int | None = None
    speed: float | None = None
    lap_number: int | None = None


class IntervalRecord(BaseModel):
    driver_number: int | None = None
    lap_number: int | None = None
    gap_to_leader: float | None = None
    interval: float | None = None


class PitRecord(BaseModel):
    driver_number: int | None = None
    lap_number: int | None = None
    pit_duration: float | None = None


class PositionRecord(BaseModel):
    driver_number: int | None = None
    lap_number: int | None = None
    position: int | None = None


class DriverRecord(BaseModel):
    driver_number: int | None = None
    full_name: str | None = None
    team_name: str | None = None
    acronym: str | None = None


class AnomalyResult(BaseModel):
    driver_number: int
    lap_number: int
    anomaly_score: float
    is_anomaly: bool
    most_anomalous_feature: str


class TireDegradationReport(BaseModel):
    compound: str
    deg_rate: float
    laps_to_cliff: int
    recommended_pit_lap: int


class EngineFlag(BaseModel):
    driver_number: int
    overheating_risk: bool
    mapping_change_detected: bool


class OvertakeEvent(BaseModel):
    lap: int
    driver: int
    position_gained: int
    zone: str
    speed_delta: float


class SectorReport(BaseModel):
    driver_number: int
    worst_sector: str
    time_loss_vs_best: float
    problem_corners: list[str] = Field(default_factory=list)


class RaceAlert(BaseModel):
    severity: Literal["CRITICAL", "WARNING", "INFO"]
    category: Literal[
        "TIRE_DEGRADATION",
        "ENGINE_TEMP",
        "BATTERY_ERS",
        "LAP_TIME_ANOMALY",
        "POSITION_CHANGE",
        "PIT_WINDOW",
    ]
    driver: int | None = None
    message: str
    timestamp: datetime


class RaceSummary(BaseModel):
    headline: str
    key_events: list[str]
    driver_reports: dict[str, dict[str, Any]]
    technical_insights: list[str]
    alert_summary: dict[str, list[str]]
