from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import db
from app.schemas.aggregates import (
    LinkResponse,
    LinkDetailResponse,
    SpatialFilterRequest,
)
from app.services import aggregates as aggregates_service

router = APIRouter()


@router.get("/", response_model=list[LinkResponse])
def get_aggregates(
    day: str = Query(..., description="Day of week"),
    period: str = Query(..., description="Time period"),
    limit: int = Query(1000, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    db: Session = Depends(db),
):
    """
    Returns aggregated average speed per link for a given day and time period.
    """

    results = aggregates_service.get_aggregated_speeds(
        db=db,
        day=day,
        period=period,
        limit=limit,
        offset=offset,
    )

    return results


@router.post("/spatial_filter", response_model=list[LinkResponse])
def spatial_filter(req: SpatialFilterRequest, db: Session = Depends(db)):
    """
    Returns road segments intersecting the bounding box for the given day and period.
    """
    day = req.day
    period = req.period
    bbox = req.bbox
    limit = req.limit
    offset = req.offset
    result = aggregates_service.get_spatial_filter(
        db=db, day=day, period=period, bbox=bbox, limit=limit, offset=offset
    )
    return result


@router.get("/{link_id}", response_model=Optional[LinkDetailResponse])
def get_aggregate_details(
    link_id: str,
    day: str = Query(..., description="Day of week"),
    period: str = Query(..., description="Time period"),
    db: Session = Depends(db),
):
    """
    Returns detailed aggregated speed information for a specific link, day, and time period.
    """

    result = aggregates_service.get_aggregated_speed_details(
        db=db,
        link_id=link_id,
        day=day,
        period=period,
    )

    return result
