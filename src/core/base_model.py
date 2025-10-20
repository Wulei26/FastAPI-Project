from datetime import datetime, timezone
from sqlalchemy import MetaData, func, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs

from core.config import db_settings

"""
让 SQLAlchemy 在创建 PostgreSQL 表（或迁移）时，把索引、主键、外键、唯一约束、检查约束的名字起成“PostgreSQL 社区风格”，而不是 SQLAlchemy 自带的随机长串。
"""
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class DateTimeMixin:
    if db_settings.db_type == "postgres":
        # PostgreSQL 原生支持 now() 和 onupdate
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
            index=True,
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    else:
        # SQLite: 使用 Python 层默认值模拟
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            # 插入时用应用层时间,生产环境推荐使用 Unix 时间戳
            default=datetime.now(timezone.utc),
            nullable=False,
            index=True,
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            default=datetime.now(timezone.utc),
            onupdate=datetime.now(timezone.utc),
            nullable=False,
        )
