from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from core.base_model import Base, DateTimeMixin


class User(Base, DateTimeMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))

    def __repr__(self) -> str:
        return f"<User(id = {self.id}, username='{self.username}')>"
