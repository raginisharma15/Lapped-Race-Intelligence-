import pandas as pd

from app.utils.schemas import SectorReport


def analyze_sectors(df: pd.DataFrame) -> list[SectorReport]:
    """Analyze sector losses and infer problem corners."""
    if df.empty:
        return []
    sector_cols = ["sector_1", "sector_2", "sector_3"]
    for col in sector_cols:
        if col not in df.columns:
            df[col] = 0.0

    best_by_sector = {col: float(df[col].dropna().min()) if df[col].notna().any() else 0.0 for col in sector_cols}
    reports: list[SectorReport] = []

    for driver, chunk in df.groupby("driver_number"):
        means = {col: float(chunk[col].fillna(chunk[col].median()).mean()) for col in sector_cols}
        losses = {col: means[col] - best_by_sector[col] for col in sector_cols}
        worst_sector = max(losses, key=losses.get)
        problem_corners = []
        if losses["sector_1"] > 0.2:
            problem_corners.append("Corners 1-4")
        if losses["sector_2"] > 0.2:
            problem_corners.append("Corners 5-10")
        if losses["sector_3"] > 0.2:
            problem_corners.append("Corners 11-16")
        reports.append(
            SectorReport(
                driver_number=int(driver),
                worst_sector=worst_sector,
                time_loss_vs_best=float(losses[worst_sector]),
                problem_corners=problem_corners,
            )
        )
    return reports
