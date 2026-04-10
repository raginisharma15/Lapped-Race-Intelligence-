import asyncio
from pathlib import Path
from typing import Any

import pandas as pd

from config import get_settings


class FastF1Service:
    """Fetch and normalize FastF1 telemetry for session analysis."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def get_telemetry(self, session_key: str) -> pd.DataFrame:
        """Return telemetry features merged at driver/lap granularity."""
        try:
            import fastf1
        except ImportError:
            return pd.DataFrame()

        raw_cache_dir = str(self.settings.fastf1_cache_dir or "").strip()
        cache_dir = Path(raw_cache_dir if raw_cache_dir else "./cache/fastf1").expanduser().resolve()
        cache_dir.mkdir(parents=True, exist_ok=True)
        print(f"FastF1 cache directory: {cache_dir}")
        fastf1.Cache.enable_cache(str(cache_dir))

        def _load() -> pd.DataFrame:
            session = fastf1.get_session(2024, session_key, "R")
            session.load(telemetry=True, laps=True, weather=False, messages=False)
            laps = session.laps[["DriverNumber", "LapNumber", "Compound", "TyreLife"]].copy()
            laps.columns = ["driver_number", "lap_number", "tyre_compound", "tyre_age"]
            return laps

        df = await asyncio.to_thread(_load)
        return df

    def merge_with_openf1(self, base_df: pd.DataFrame, fastf1_df: pd.DataFrame) -> pd.DataFrame:
        """Merge FastF1 and OpenF1 frames by driver and lap."""
        if fastf1_df.empty:
            base_df["tyre_compound"] = base_df.get("tyre_compound", "UNKNOWN")
            base_df["tyre_age"] = base_df.get("tyre_age", 0)
            return base_df
        return base_df.merge(fastf1_df, how="left", on=["driver_number", "lap_number"])
