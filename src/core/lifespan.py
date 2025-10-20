from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
from core.config import redis_settings
import redis.asyncio as Redis
from core.database import setup_database_connection, close_database_connection, create_db_and_tables, get_db
from core.config import app_settings

"""
USE lifespan state instated of app.state
"""


class AppState:
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_database_connection()
    if app_settings.app_env == "dev":
        await create_db_and_tables()
    logger.info("🚀 数据库已连接")
    yield
    await close_database_connection()
    logger.info("应用关闭，数据库连接已释放")
