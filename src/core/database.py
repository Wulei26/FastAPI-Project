from core.config import db_settings
from typing import Optional
from loguru import logger
from typing import AsyncGenerator
from core.base_model import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

##创建异步数据库会话引擎和会话工厂

_ASYNC_ENGINE: Optional[AsyncEngine] = None
# create_async_engine(url=db_settings.ASYNC_SQLALCHEMY_DATABASE_URL, **db_settings.ASYNC_ENGINE_OPTION)

# _SessionFactory: Optional[async_sessionmaker[AsyncSession]] = None


# # 数据库依赖注入
# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with _SessionFactory() as session:
#         yield session


# ## 创建数据库表的函数
# async def init_and_create_db():
#     async with _ASYNC_ENGINE.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#         logger.info("数据库表初始化成功👍")


async def setup_database_connection():
    """启动应用，初始化会话引擎和会话工厂"""
    global _ASYNC_ENGINE, _SessionFactory
    if _ASYNC_ENGINE is not None:
        logger.info("数据库已经初始化，跳过重复设置")
        return
    logger.info("正在创建数据库引擎")
    _ASYNC_ENGINE = create_async_engine(
        url=db_settings.ASYNC_SQLALCHEMY_DATABASE_URL, **db_settings.ASYNC_ENGINE_OPTION
    )
    _SessionFactory = async_sessionmaker(
        class_=AsyncSession, autoflush=False, expire_on_commit=False, bind=_ASYNC_ENGINE
    )
    logger.info("数据库引擎和会话工厂已成功创建。")


async def close_database_connection():
    """在应用关闭时，关闭全局的数据库引擎连接池。"""
    global _ASYNC_ENGINE, _SessionFactory
    if _ASYNC_ENGINE:
        await _ASYNC_ENGINE.dispose()
        _ASYNC_ENGINE = None
        _SessionFactory = None
        logger.info("数据库引擎连接池已关闭。")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖注入函数，为每个请求提供一个独立的数据库会话。
    """
    if _SessionFactory is None:
        raise RuntimeError("数据库会话工厂未初始化！")

    # 从会话工厂中创建一个新的会话
    async with _SessionFactory() as session:
        # 使用 yield 将会话提供给路径函数
        yield session


# --- 4. 辅助工具：创建数据库表 ---
async def create_db_and_tables():
    """
    一个开发工具，用于在应用启动前创建所有定义的数据库表。
    注意：在生产环境中你可能需要更专业的迁移工具如 Alembic。
    """
    if not _ASYNC_ENGINE:
        raise RuntimeError("数据库引擎未初始化，无法创建表。")
    async with _ASYNC_ENGINE.begin() as conn:
        # 让 SQLAlchemy 根据所有继承了 Base 的模型类去创建表
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表已成功同步/创建。")
