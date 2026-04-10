import asyncio
from typing import Any

import httpx

from config import get_settings
from app.utils.cache import TTLCache
from app.utils.schemas import (
    CarDataRecord,
    DriverRecord,
    IntervalRecord,
    LapRecord,
    PitRecord,
    PositionRecord,
)


class OpenF1Service:
    """Async OpenF1 client with retry and TTL cache."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = TTLCache[list[dict[str, Any]]](ttl_seconds=60)

    async def _fetch(self, endpoint: str, session_key: str) -> list[dict[str, Any]]:
        cache_key = f"{endpoint}:{session_key}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"{self.settings.openf1_base_url}/{endpoint}"
        params = {"session_key": session_key}
        backoff = 0.5
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    payload = response.json()
                    if not isinstance(payload, list):
                        return []
                    self.cache.set(cache_key, payload)
                    return payload
            except httpx.HTTPError:
                if attempt == 2:
                    return []
                await asyncio.sleep(backoff)
                backoff *= 2
        return []

    async def get_laps(self, session_key: str) -> list[LapRecord]:
        data = await self._fetch("laps", session_key)
        return [
            LapRecord(
                driver_number=item.get("driver_number"),
                lap_number=item.get("lap_number"),
                lap_time=item.get("lap_duration"),
                sector_1=item.get("duration_sector_1"),
                sector_2=item.get("duration_sector_2"),
                sector_3=item.get("duration_sector_3"),
            )
            for item in data
        ]

    async def get_car_data(self, session_key: str) -> list[CarDataRecord]:
        data = await self._fetch("car_data", session_key)
        return [
            CarDataRecord(
                driver_number=item.get("driver_number"),
                rpm=item.get("rpm"),
                throttle=item.get("throttle"),
                brake=item.get("brake"),
                drs=item.get("drs"),
                n_gear=item.get("n_gear"),
                speed=item.get("speed"),
                lap_number=item.get("lap_number"),
            )
            for item in data
        ]

    async def get_intervals(self, session_key: str) -> list[IntervalRecord]:
        data = await self._fetch("intervals", session_key)
        return [
            IntervalRecord(
                driver_number=item.get("driver_number"),
                lap_number=item.get("lap_number"),
                gap_to_leader=item.get("gap_to_leader"),
                interval=item.get("interval"),
            )
            for item in data
        ]

    async def get_pit(self, session_key: str) -> list[PitRecord]:
        data = await self._fetch("pit", session_key)
        return [
            PitRecord(
                driver_number=item.get("driver_number"),
                lap_number=item.get("lap_number"),
                pit_duration=item.get("pit_duration"),
            )
            for item in data
        ]

    async def get_position(self, session_key: str) -> list[PositionRecord]:
        data = await self._fetch("position", session_key)
        return [
            PositionRecord(
                driver_number=item.get("driver_number"),
                lap_number=item.get("lap_number"),
                position=item.get("position"),
            )
            for item in data
        ]

    async def get_drivers(self, session_key: str) -> list[DriverRecord]:
        data = await self._fetch("drivers", session_key)
        return [
            DriverRecord(
                driver_number=item.get("driver_number"),
                full_name=item.get("full_name"),
                team_name=item.get("team_name"),
                acronym=item.get("name_acronym"),
            )
            for item in data
        ]
