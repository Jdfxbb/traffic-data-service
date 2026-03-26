from pydantic import BaseModel
from typing import Optional


class LinkResponse(BaseModel):
    link_id: int
    road_name: Optional[str]
    average_speed: float
    length: float
    geometry: dict


class LinkDetailResponse(BaseModel):
    link_id: int
    road_name: Optional[str]
    average_speed: float
    length: float
    geometry: dict
    period: str
    day: str


class SpatialFilterRequest(BaseModel):
    day: str
    period: str
    bbox: list[float]
    limit: Optional[int] = 1000
    offset: Optional[int] = 0
