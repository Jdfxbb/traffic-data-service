from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import db
from app.schemas.aggregates import LinkResponse
from app.services import patterns as patterns_service

router = APIRouter()


@router.get("/slow_links", response_model=list[LinkResponse])
def get_slow_links(
    period: str = Query(..., description="Time period"),
    threshold: float = Query(..., description="Speed threshold"),
    min_days: int = Query(1, description="Minimum number of days below threshold"),
    limit: int = Query(1000, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    db: Session = Depends(db),
):
    """
    Returns aggregated average speed per link
    for a given day and time period.
    """

    results = patterns_service.get_slow_links(
        db=db,
        period=period,
        threshold=threshold,
        min_days=min_days,
        limit=limit,
        offset=offset,
    )

    return results
