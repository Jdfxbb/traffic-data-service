from app.models.traffic import Link, SpeedRecord
from sqlalchemy import func
from app.config import TIME_PERIODS
import json
from geoalchemy2.functions import ST_AsGeoJSON


def get_slow_links(
    db, period: str, threshold: float, min_days: int, limit: int = 1000, offset: int = 0
):
    """
    Returns Links with average speeds below a threshold for at least min_days in a week
    """

    period_int = TIME_PERIODS.get(period.lower())

    if period_int is None:
        raise ValueError(f"Invalid period '{period}'")

    # average speed per link per day for the given period
    daily_avg = (
        db.query(
            SpeedRecord.link_id,
            SpeedRecord.day_of_week,
            func.avg(SpeedRecord.average_speed).label("daily_avg_speed"),
        )
        .filter(SpeedRecord.period == period_int)
        .group_by(SpeedRecord.link_id, SpeedRecord.day_of_week)
        .subquery()
    )

    # count days where daily average is below threshold
    slow_days = (
        db.query(
            daily_avg.c.link_id,
            func.count(daily_avg.c.day_of_week).label("days_below_threshold"),
            func.avg(daily_avg.c.daily_avg_speed).label("average_speed"),
        )
        .filter(daily_avg.c.daily_avg_speed < threshold)
        .group_by(daily_avg.c.link_id)
        .having(func.count(daily_avg.c.day_of_week) >= min_days)
        .subquery()
    )

    # join to links to get geometry and metadata
    results = (
        db.query(
            Link.id.label("link_id"),
            Link.road_name,
            Link.length,
            ST_AsGeoJSON(Link.geometry).label("geometry"),
            slow_days.c.days_below_threshold,
            slow_days.c.average_speed,
        )
        .join(slow_days, Link.id == slow_days.c.link_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "link_id": r.link_id,
            "road_name": r.road_name,
            "length": r.length,
            "average_speed": round(r.average_speed, 2),
            "days_below_threshold": r.days_below_threshold,
            "geometry": json.loads(r.geometry),
        }
        for r in results
    ]
