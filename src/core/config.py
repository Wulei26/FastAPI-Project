# config.py
import sys
import os
from configparser import ConfigParser
from typing import Literal
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


def _get_env_file() -> str:
    """
    根据运行上下文确定应加载的 .env 文件路径。
    支持 alembic、uvicorn 和普通脚本三种场景。
    """
    # 场景1: alembic 迁移
    if "alembic" in sys.argv[0] or any("alembic" in arg for arg in sys.argv):
        config = ConfigParser()
        config.read("alembic.ini", encoding="utf-8")
        env_name = config.get("settings", "env", fallback="dev")
        return f".env.{env_name}"

    # 场景2: uvicorn 启动（如通过命令行或 ASGI 服务器）
    if "uvicorn" in sys.argv[0] or "uvicorn" in sys.modules:
        return f".env.{os.getenv('APP_ENV', 'dev')}"

    # 场景3: 普通脚本运行（如 python main.py --env prod）
    try:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--env", type=str, default="dev")
        args, _ = parser.parse_known_args()
        env_name = args.env or "dev"
        return f".env.{env_name}"
    except Exception:
        # 解析失败时回退到 dev
        return ".env.dev"


# ✅ 只调用一次，所有配置类共享同一个 .env 文件路径
_ENV_FILE = _get_env_file()


class AppSettings(BaseSettings):
    """应用基础配置"""

    app_env: str = "dev"
    app_name: str = "FastAPI-demo"
    app_version: str = "V1.0"
    app_root_path: str = "/dev-api"
    app_host: str = "127.0.0.1"
    app_port: int = 9099
    app_reload: bool = True

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class DBSettings(BaseSettings):
    """数据库配置"""

    db_type: Literal["mysql", "postgresql"] = "postgresql"
    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_username: str = "postgres"
    db_password: str = "terry123"
    db_database: str = "fastapi-demo"

    # 连接池配置
    db_pool_size: int = 50
    db_pool_timeout: int = 30
    db_max_overflow: int = 10
    db_pool_pre_ping: bool = False
    db_pool_use_lifo: bool = False
    db_pool_recycle: int = 3600
    db_echo: bool = True

    @computed_field  # 告诉 Pydantic：这个字段是通过代码计算出来的，不需要从外部输入（如 JSON、.env）解析。
    @property  # 将一个方法伪装成“属性”，调用时无需加 ()
    def ASYNC_SQLALCHEMY_DATABASE_URL(self) -> str:
        ASYNC_SQLALCHEMY_DATABASE_URL = (
            f"mysql+asyncmy://{self.db_username}:{quote_plus(self.db_password)}@"
            f"{self.db_host}:{self.db_port}/{self.db_database}"
        )
        if self.db_type == "postgresql":
            ASYNC_SQLALCHEMY_DATABASE_URL = (
                f"postgresql+asyncpg://{self.db_username}:{quote_plus(self.db_password)}@"
                f"{self.db_host}:{self.db_port}/{self.db_database}"
            )
        return ASYNC_SQLALCHEMY_DATABASE_URL

    @computed_field
    @property
    def ASYNC_ENGINE_OPTION(self) -> dict:
        """根据数据库类型生成 SQLAlchemy 异步引擎配置"""
        return {
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "pool_timeout": self.db_pool_timeout,
            "pool_recycle": self.db_pool_recycle,
            "pool_pre_ping": self.db_pool_pre_ping,
            "echo": self.db_echo,
        }

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,  ##大小写不敏感
    )


class RedisSettings(BaseSettings):
    """
    Redis配置
    """

    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_username: str = ""
    redis_password: str = ""
    redis_database: int = 2
    redis_database_kc: int = 3

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_database}:"


# 或者分别导出（更推荐，显式清晰）
app_settings = AppSettings()
db_settings = DBSettings()
redis_settings = RedisSettings()
