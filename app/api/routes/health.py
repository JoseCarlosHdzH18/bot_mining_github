from fastapi import APIRouter, Response
from sqlalchemy import text
import redis
from app.db.session import engine
from app.config import REDIS_URL

router = APIRouter()


@router.get("/")
def health():
    return {"status": "ok"}


@router.get("/ready")
def health_ready():
    checks = {}
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
    
    try:
        r = redis.from_url(REDIS_URL)
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"
    
    all_ok = all(v == "ok" for v in checks.values())
    
    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks
    }
