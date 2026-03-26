# Traffic Data Service

A FastAPI microservice that ingests geospatial traffic speed data, stores it in PostgreSQL + PostGIS, and exposes REST endpoints for spatial and temporal aggregation. Includes a Jupyter notebook for Mapbox visualization.

---

## Stack

- **FastAPI** — REST API
- **PostgreSQL + PostGIS** — spatial data storage and querying
- **SQLAlchemy + GeoAlchemy2** — ORM and geometry support
- **Docker + Docker Compose** — containerized local environment
- **Jupyter + MapboxGL** — visualization notebook

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- A Mapbox access token ([get one free at mapbox.com](https://mapbox.com))

### 1. Clone the repo

```bash
git clone <repo-url>
cd traffic-data-service
```

### 2. Add environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your database URL if needed. Defaults work out of the box with Docker Compose.

### 3. Add data files

Place the two Parquet datasets in the `data/` directory:

```
data/
├── link_info.parquet.gz
└── duval_jan1_2024.parquet.gz
```

### 4. Start the service

```bash
docker-compose up --build
```

Docker Compose will:

1. Start PostgreSQL + PostGIS and wait until healthy
2. Run `init_db.py` to create tables and ingest data (skipped automatically on subsequent runs)
3. Start the FastAPI service at `http://localhost:8000`

---

## API Endpoints

Interactive docs available at `http://localhost:8000/docs`

### `GET /api/v1/aggregates/`

Returns aggregated average speed per link for a given day and time period.

**Query params:** `day`, `period`, `limit` (default 100), `offset` (default 0)

```bash
curl "http://localhost:8000/api/v1/aggregates/?day=Monday&period=AM Peak"
```

---

### `GET /api/v1/aggregates/{link_id}`

Returns speed and metadata for a single road segment.

**Query params:** `day`, `period`

```bash
curl "http://localhost:8000/api/v1/aggregates/123?day=Monday&period=AM Peak"
```

---

### `GET /api/v1/patterns/slow_links/`

Returns links with average speeds below a threshold for at least `min_days` in a week.

**Query params:** `period`, `threshold`, `min_days`, `limit` (default 100), `offset` (default 0)

```bash
curl "http://localhost:8000/api/v1/patterns/slow_links/?period=AM Peak&threshold=25&min_days=3"
```

---

### `POST /api/v1/aggregates/spatial_filter/`

Returns road segments intersecting a bounding box for a given day and period. Spatial filtering is handled natively by PostGIS via `ST_Intersects`.

```bash
curl -X POST "http://localhost:8000/api/v1/aggregates/spatial_filter/" \
  -H "Content-Type: application/json" \
  -d '{
    "day": "Wednesday",
    "period": "AM Peak",
    "bbox": [-81.8, 30.1, -81.6, 30.3]
  }'
```

---

## Valid Parameters

**Days:** Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday

**Periods:**

| ID  | Name            | Hours         |
| --- | --------------- | ------------- |
| 1   | Overnight       | 00:00 – 03:59 |
| 2   | Early Morning   | 04:00 – 06:59 |
| 3   | AM Peak         | 07:00 – 09:59 |
| 4   | Midday          | 10:00 – 12:59 |
| 5   | Early Afternoon | 13:00 – 15:59 |
| 6   | PM Peak         | 16:00 – 18:59 |
| 7   | Evening         | 19:00 – 23:59 |

---

## Notebook

The Jupyter notebook in `notebooks/` demonstrates all four endpoints with Mapbox visualizations.

### Setup

```bash
pip install jupyter requests pandas mapboxgl
jupyter notebook
```

Open `notebooks/visualization.ipynb` and set your Mapbox token in the Setup cell:

```python
MAPBOX_TOKEN = "your_token_here"
```

> **Note:** `mapboxgl` has a known incompatibility with IPython 8.x. If you encounter an `ImportError` on `IPython.core.display`, apply this fix:
>
> ```bash
> find . -path "*/mapboxgl/viz.py" -exec sed -i '' 's/from IPython.core.display/from IPython.display/g' {} +
> ```

---

## Project Structure

```
traffic-data-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── aggregates.py     # Aggregate endpoints
│   │       ├── patterns.py       # Pattern endpoints
│   │       └── router.py         # Route registration
│   ├── database/
│   │   ├── ingest.py             # Parquet → PostGIS loader
│   │   ├── init_db.py            # Table creation + ingestion entrypoint
│   │   └── session.py            # DB engine and session factory
│   ├── models/
│   │   └── traffic.py            # SQLAlchemy ORM models (Link, SpeedRecord)
│   ├── schemas/
│   │   └── aggregates.py         # Pydantic request/response schemas
│   ├── services/
│   │   ├── aggregates.py         # Aggregation query logic
│   │   └── patterns.py           # Pattern query logic
│   ├── config.py                 # Settings via pydantic-settings
│   └── main.py                   # FastAPI app entry point
├── data/                         # Parquet source files (not committed)
├── notebooks/
│   └── traffic_service.ipynb       # Mapbox visualization notebook
├── diagrams/
│   └── architecture_diagram.png          # Architecture diagram
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
```

---

## Architecture

![Architecture Diagram](architecture_diagram.png)

---

## Design Notes

**Idempotent ingestion** — `init_db.py` checks for existing data before ingesting. On container restart, ingestion is skipped automatically. A production implementation would use Alembic for schema migrations and upsert logic (`INSERT ... ON CONFLICT DO UPDATE`) for incremental data loads.

**Pagination** — all list endpoints support `limit` and `offset` query parameters. The dataset contains ~100,000 links and returning all records in a single response is not appropriate for production use. This could be mitigated by zoom-level filtering on maps and database-side data rollups for summaries (.e.g. for a dashboard)

**Geometry storage** — link geometries are stored as PostGIS `MULTILINESTRING` (SRID 4326) to enable native spatial operations. `ST_Intersects` powers the bounding box filter endpoint. `ST_AsGeoJSON` is used at the service layer to convert back to GeoJSON for API responses.

**Two-stage aggregation in slow links** — the `/patterns/slow_links/` query averages speed per link per day before counting days below threshold, avoiding false inflation from multiple records on the same day.
