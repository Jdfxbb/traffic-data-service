from app.models.traffic import Link, SpeedRecord
from sqlalchemy import func
from app.config import DAY_OF_WEEK, TIME_PERIODS
from geoalchemy2.functions import ST_AsGeoJSON
import json


def get_aggregated_speeds(
    db, day: str, period: str, limit: int = 1000, offset: int = 0
):
    """
    Returns aggregated average speed per link for a given day and time period.
    """

    day_int = DAY_OF_WEEK.get(day.lower())
    period_int = TIME_PERIODS.get(period.lower())

    if day_int is None or period_int is None:
        raise ValueError(f"Invalid day '{day}' or period '{period}'")

    results = (
        db.query(
            Link.id,
            Link.road_name,
            Link.length,
            ST_AsGeoJSON(Link.geometry).label("geometry"),
            func.avg(SpeedRecord.average_speed).label("average_speed"),
        )
        .join(SpeedRecord, Link.id == SpeedRecord.link_id)
        .filter(SpeedRecord.day_of_week == day_int)
        .filter(SpeedRecord.period == period_int)
        .group_by(Link.id)
        .order_by(Link.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "link_id": r.id,
            "road_name": r.road_name,
            "length": r.length,
            "average_speed": round(r.average_speed, 2),
            "geometry": json.loads(r.geometry),
        }
        for r in results
    ]


def get_aggregated_speed_details(db, link_id: str, day: str, period: str):
    """
    Returns detailed aggregated speed information for a specific link, day, and time period.
    """

    day_int = DAY_OF_WEEK.get(day.lower())
    period_int = TIME_PERIODS.get(period.lower())

    if day_int is None or period_int is None:
        raise ValueError(f"Invalid day '{day}' or period '{period}'")

    result = (
        db.query(
            Link.id,
            Link.road_name,
            Link.length,
            ST_AsGeoJSON(Link.geometry).label("geometry"),
            func.avg(SpeedRecord.average_speed).label("average_speed"),
        )
        .join(SpeedRecord, Link.id == SpeedRecord.link_id)
        .filter(Link.id == link_id)
        .filter(SpeedRecord.day_of_week == day_int)
        .filter(SpeedRecord.period == period_int)
        .group_by(Link.id)
        .first()
    )

    if not result:
        return None

    return {
        "link_id": result.id,
        "road_name": result.road_name,
        "length": result.length,
        "geometry": json.loads(result.geometry),
        "average_speed": round(result.average_speed, 2),
        "day": day,
        "period": period,
    }


def get_spatial_filter(
    db, day: str, period: str, bbox: list[float], limit: int = 1000, offset: int = 0
):
    """
    Returns:
    Road segments intersecting the bounding box for the given day and period.
    """
    minx, miny, maxx, maxy = bbox

    day_int = DAY_OF_WEEK.get(day.lower())
    period_int = TIME_PERIODS.get(period.lower())

    if day_int is None or period_int is None:
        raise ValueError(f"Invalid day '{day}' or period '{period}'")

    results = (
        db.query(
            Link.id,
            Link.road_name,
            Link.length,
            ST_AsGeoJSON(Link.geometry).label("geometry"),
            func.avg(SpeedRecord.average_speed).label("average_speed"),
        )
        .join(SpeedRecord, Link.id == SpeedRecord.link_id)
        .filter(SpeedRecord.day_of_week == day_int)
        .filter(SpeedRecord.period == period_int)
        .filter(
            func.ST_Intersects(
                Link.geometry,
                func.ST_MakeEnvelope(minx, miny, maxx, maxy, 4326),
            )
        )
        .group_by(Link.id)
        .order_by(Link.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "link_id": r.id,
            "road_name": r.road_name,
            "length": r.length,
            "average_speed": round(r.average_speed, 2),
            "geometry": json.loads(r.geometry),
        }
        for r in results
    ]
