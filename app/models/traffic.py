from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from sqlalchemy.schema import Index

from app.database.session import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    road_name = Column(String)
    length = Column(Float)

    geometry = Column(
        Geometry(
            geometry_type="MULTILINESTRING",
            srid=4326,
        ),
        nullable=False,
    )


class SpeedRecord(Base):
    __tablename__ = "speed_records"

    id = Column(Integer, primary_key=True)

    link_id = Column(Integer, ForeignKey("links.id"), index=True)

    date_time = Column(DateTime)
    average_speed = Column(Float)

    day_of_week = Column(Integer, index=True)
    period = Column(Integer, index=True)

    link = relationship("Link")


Index("idx_links_geom", Link.geometry, postgresql_using="gist")
