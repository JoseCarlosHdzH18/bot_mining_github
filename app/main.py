from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis
from sqlalchemy import text

from app.api.router import router
from app.db.session import init_db, engine
from app.config import REDIS_URL
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    try:
        r = redis.from_url(REDIS_URL)
        r.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
    
    yield
    
    logger.info("Shutting down application...")


app = FastAPI(
    title="GitHub Miner Bot",
    description="Distributed GitHub mining system with Dolibarr integration",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)
