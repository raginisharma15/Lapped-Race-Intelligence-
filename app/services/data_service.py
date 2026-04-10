from typing import Any

import requests

OPENF1_LAPS_URL = "https://api.openf1.org/v1/laps?session_key=latest"


def fetch_lap_data() -> dict[str, Any]:
    try:
        response = requests.get(OPENF1_LAPS_URL, timeout=10)
        response.raise_for_status()
        laps = response.json()
    except requests.RequestException:
        return {"message": "Failed to fetch lap data from OpenF1 API"}
    except ValueError:
        return {"message": "Invalid response received from OpenF1 API"}

    if not isinstance(laps, list):
        return {"message": "Unexpected response format from OpenF1 API"}

    simplified_laps: list[dict[str, Any]] = []
    for lap in laps[:10]:
        if not isinstance(lap, dict):
            continue
        simplified_laps.append(
            {
                "driver_number": lap.get("driver_number"),
                "lap_time": lap.get("lap_duration"),
                "sector_1": lap.get("duration_sector_1"),
                "sector_2": lap.get("duration_sector_2"),
                "sector_3": lap.get("duration_sector_3"),
            }
        )

    return {"laps": simplified_laps}
