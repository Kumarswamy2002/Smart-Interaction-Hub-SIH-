from fastapi import APIRouter
from sih.domain.observability.service import observability_platform

router = APIRouter(prefix="/system", tags=["System & Observability"])

@router.get("/health")
def health_check():
    return observability_platform.get_health()

@router.get("/metrics")
def get_metrics():
    return observability_platform.get_metrics_summary()
