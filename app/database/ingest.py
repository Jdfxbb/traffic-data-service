from sqlalchemy import text
import pandas as pd
from app.config import LINK_PARQUET_PATH, SPEED_RECORDS_PARQUET_PATH
from app.models.traffic import Link, SpeedRecord
from app.main import logger


def ingest_link_data(db):
    """Ingests link data from a Parquet file into the database."""
    existing = db.query(Link).first()
    if existing:
        # note: for demo purposes, this assumes that if any data exists, then all data is loaded
        # to speed up docker rebuilds. In production, data ingestion would be independent of the app lifecycle
        logger.warning("Data already loaded, skipping ingestion")
        return

    df = pd.read_parquet(LINK_PARQUET_PATH)

    # stage via temp table to leverage pandas parquet parsing,
    # then insert with ST_GeomFromGeoJSON for geometry conversion
    df.to_sql("links_raw", db.bind, if_exists="replace", index=False)

    db.execute(text("""
            INSERT INTO links (id, road_name, length, geometry)
            SELECT
                link_id as "id",
                road_name,
                _length::float as "length",
                ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(geo_json),4326))
            FROM links_raw
            ON CONFLICT (id) DO NOTHING
            -- skip dupes for demo, in prod we would handle updates
            --ON CONFLICT (id) DO UPDATE SET
            --    road_name = EXCLUDED.road_name,
            --    geometry = EXCLUDED.geometry,
            --    length = EXCLUDED.length
        """))

    db.commit()

    # clean up temp table
    db.execute(text("DROP TABLE IF EXISTS links_raw"))
    db.commit()


def ingest_speed_records(db):
    """Ingests speed records from a Parquet file into the database."""
    existing = db.query(SpeedRecord).first()
    if existing:
        logger.info("Data already loaded, skipping ingestion")
        return

    speed_df = pd.read_parquet(SPEED_RECORDS_PARQUET_PATH)

    speed_df["date_time"] = pd.to_datetime(speed_df["date_time"])

    speed_df = speed_df[
        [
            "link_id",
            "date_time",
            "average_speed",
            "day_of_week",
            "period",
        ]
    ]

    speed_df.to_sql(
        "speed_records",
        db.bind,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=10000,
    )
