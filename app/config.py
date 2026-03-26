import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/traffic",
)

LINK_PARQUET_PATH = os.getenv("LINK_PARQUET_PATH", "/data/link_info.parquet.gz")

SPEED_RECORDS_PARQUET_PATH = os.environ.get(
    "SPEED_RECORDS_PARQUET_PATH", "/data/duval_jan1_2024.parquet.gz"
)

TIME_PERIODS = {
    "overnight": 1,
    "early morning": 2,
    "am peak": 3,
    "midday": 4,
    "early afternoon": 5,
    "pm peak": 6,
    "evening": 7,
}

DAY_OF_WEEK = {
    "sunday": 1,
    "monday": 2,
    "tuesday": 3,
    "wednesday": 4,
    "thursday": 5,
    "friday": 6,
    "saturday": 7,
}
