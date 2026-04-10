import asyncio

import pandas as pd

from app.services.fastf1_service import FastF1Service
from app.services.openf1_service import OpenF1Service


async def get_session_dataframe(session_key: str) -> pd.DataFrame:
    """Build a unified telemetry dataframe for a session."""
    openf1 = OpenF1Service()
    fastf1 = FastF1Service()

    laps_task = openf1.get_laps(session_key)
    car_task = openf1.get_car_data(session_key)
    interval_task = openf1.get_intervals(session_key)
    position_task = openf1.get_position(session_key)
    fastf1_task = fastf1.get_telemetry(session_key)

    laps, car_data, intervals, positions, fastf1_df = await asyncio.gather(
        laps_task, car_task, interval_task, position_task, fastf1_task
    )

    laps_df = pd.DataFrame([item.model_dump() for item in laps])
    if laps_df.empty:
        return pd.DataFrame(
            columns=[
                "driver_number",
                "lap_number",
                "lap_time",
                "sector_1",
                "sector_2",
                "sector_3",
                "tyre_compound",
                "tyre_age",
                "speed_trap",
                "throttle_pct",
                "brake_pct",
                "engine_rpm",
                "drs_active",
                "gap_to_leader",
                "position",
            ]
        )

    car_df = pd.DataFrame([item.model_dump() for item in car_data])
    if not car_df.empty:
        car_agg = (
            car_df.groupby(["driver_number", "lap_number"], as_index=False)
            .agg(
                speed_trap=("speed", "max"),
                throttle_pct=("throttle", "mean"),
                brake_pct=("brake", "mean"),
                engine_rpm=("rpm", "mean"),
                drs_active=("drs", "max"),
            )
            .fillna(0)
        )
    else:
        car_agg = pd.DataFrame(columns=["driver_number", "lap_number"])

    intervals_df = pd.DataFrame([item.model_dump() for item in intervals])
    if not intervals_df.empty:
        intervals_df = intervals_df[["driver_number", "lap_number", "gap_to_leader"]]

    positions_df = pd.DataFrame([item.model_dump() for item in positions])
    if not positions_df.empty:
        positions_df = positions_df[["driver_number", "lap_number", "position"]]

    merged = laps_df.merge(car_agg, how="left", on=["driver_number", "lap_number"])
    if not intervals_df.empty:
        merged = merged.merge(intervals_df, how="left", on=["driver_number", "lap_number"])
    else:
        merged["gap_to_leader"] = None
    if not positions_df.empty:
        merged = merged.merge(positions_df, how="left", on=["driver_number", "lap_number"])
    else:
        merged["position"] = None

    merged = fastf1.merge_with_openf1(merged, fastf1_df)

    for col, default in {"tyre_compound": "UNKNOWN", "tyre_age": 0}.items():
        if col not in merged.columns:
            merged[col] = default
    merged["tyre_compound"] = merged["tyre_compound"].fillna("UNKNOWN")
    merged["tyre_age"] = merged["tyre_age"].fillna(0)

    return merged[
        [
            "driver_number",
            "lap_number",
            "lap_time",
            "sector_1",
            "sector_2",
            "sector_3",
            "tyre_compound",
            "tyre_age",
            "speed_trap",
            "throttle_pct",
            "brake_pct",
            "engine_rpm",
            "drs_active",
            "gap_to_leader",
            "position",
        ]
    ]
