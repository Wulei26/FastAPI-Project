from core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from heroes.heroes_repository import HeroRepository


class HeroService:
    def __init__(self, repository: HeroRepository) -> None:
        self.repository = repository


async def get_hero_service(self, session: AsyncSession = Depends(get_db)) -> HeroService:
    """这是一个依赖函数，负责组装并返回 HeroService 的实例。"""
    # 步骤 1: 用依赖注入的 session 创建 repository
    repository = HeroRepository(session)
    # 步骤 2: 用创建好的 repository 创建 service
    return HeroService(repository)
