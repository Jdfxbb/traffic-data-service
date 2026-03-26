from fastapi import FastAPI
from app.api.v1.router import router as api_router
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level="INFO")


def create_app() -> FastAPI:
    app = FastAPI(title="Urban SDK Traffic Service", version="1.0.0")

    # Register routers
    app.include_router(api_router)

    return app


app = create_app()


@app.get("/health")
def health():
    return {"status": "ok"}
