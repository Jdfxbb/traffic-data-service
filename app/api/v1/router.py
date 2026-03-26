from fastapi import APIRouter
from app.api.v1 import aggregates, patterns

router = APIRouter()

router.include_router(aggregates.router, prefix="/aggregates", tags=["aggregates"])

router.include_router(patterns.router, prefix="/patterns", tags=["patterns"])
