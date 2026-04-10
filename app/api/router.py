from fastapi import APIRouter
from app.api.routes import health, metrics, scraper, status, control

router = APIRouter()

router.include_router(health.router, prefix="/health")
router.include_router(metrics.router, prefix="/metrics")
router.include_router(scraper.router, prefix="/scraper")
router.include_router(status.router, prefix="/status")
router.include_router(control.router, prefix="/control")
