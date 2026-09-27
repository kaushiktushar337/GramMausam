from datetime import datetime, timezone

from app.services.weather_service import REAL_DATA


def create_alerts() -> list[dict]:
    alerts = []

    latest_indices = (
        REAL_DATA.groupby("gpcode")["date"].idxmax()
    )

    latest_rows = REAL_DATA.loc[latest_indices]

    for row in latest_rows.itertuples(index=False):
        rainfall = max(
            0.0,
            float(row.final_rainfall_mm),
        )

        if rainfall < 25:
            continue

        prediction_date = row.date
        panchayat = str(row.gpname)

        alerts.append(
            {
                "id": (
                    f"{row.gpcode}-"
                    f"{prediction_date.isoformat()}-rain"
                ),
                "panchayat": panchayat,
                "priority": (
                    "High"
                    if rainfall >= 30
                    else "Medium"
                ),
                "category": "Heavy Rainfall",
                "title": (
                    f"Heavy rainfall estimated in "
                    f"{panchayat}"
                ),
                "description": (
                    f"The rainfall model estimated "
                    f"{rainfall:.1f} mm for "
                    f"{panchayat} on "
                    f"{prediction_date:%d %b %Y}."
                ),
                "action": (
                    "Review field drainage and irrigation "
                    "plans against current local conditions."
                ),
                "time": (
                    f"Prediction date: "
                    f"{prediction_date:%d %b %Y}"
                ),
                "created_at": datetime.combine(
                    prediction_date,
                    datetime.min.time(),
                    tzinfo=timezone.utc,
                ),
            }
        )

    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }

    alerts.sort(
        key=lambda item: (
            priority_order[item["priority"]],
            item["created_at"],
            item["panchayat"],
        )
    )

    return alerts