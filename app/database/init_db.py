from sqlalchemy import text
from app.database.session import engine, Base, SessionLocal as session
from app.database.ingest import ingest_link_data, ingest_speed_records
from app.models import traffic  # noqa: F401  # Ensure models are registered
from app.main import logger


def create_tables():
    Base.metadata.create_all(bind=engine)


def main():
    logger.info("Beginning database initialization...")

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    logger.info("Creating database tables...")
    create_tables()

    with session() as db:
        logger.info("Ingesting link data...")
        ingest_link_data(db)
        logger.info("Ingesting speed records...")
        ingest_speed_records(db)
        db.commit()
        logger.info("Database initialization complete.")


if __name__ == "__main__":
    main()
