from typing import List
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import AlreadyExistsException, NotFoundException, OperationFailedException
from app.models.heroes import Hero
from app.schemas.heroes import HeroCreate, HeroUpdate


class HeroRepository:
    """Repository for handling hero database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, hero_data: HeroCreate) -> Hero:
        hero = Hero(**hero_data.model_dump())
        try:
            self.session.add(hero)  # 将新创建的 hero 对象放入 SQLAlchemy 的“暂存区”。
            await self.session.commit()  # 将“暂存区”的所有更改一次性提交到数据库，这是一个原子操作。
            await self.session.refresh(
                hero
            )  #  提交后，我们的提交的hero， Python对象其实并不知道数据库为它生成的 id 是多少。refresh 操作会用数据库中的最新数据（包括自增的 id）来更新这个 Python 对象。
            return hero
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistsException(f"Hero with alias {hero_data.alias} already exists")

    async def get_by_id(self, hero_id: int) -> Hero:
        hero = await self.session.get(Hero, hero_id)
        if not hero:
            raise NotFoundException(f"Hero with id {hero_id} not found")
        return hero

    async def get_all(self) -> List[Hero]:
        query = select(Hero)
        result = await self.session.scalars(query)
        return list(result.all())

    async def update(self, hero_data: HeroUpdate, hero_id: int) -> Hero:
        hero = await self.get_by_id(hero_id)
        update_data = hero_data.model_dump(
            exclude_unset=True
        )  # 只把用户在请求中明确传递的字段导出为字典，那些没传的（即保持默认值的）字段就忽略它们

        if not update_data:
            raise ValueError("No fields to update")

        for key, value in update_data.items():
            setattr(hero, key, value)

        try:
            await self.session.commit()
            await self.session.refresh(hero)
        except OperationFailedException:
            await self.session.rollback()
            raise OperationFailedException(f"操作失败")
        return hero

    async def delete(self, hero_id: int) -> None:
        hero = await self.get_by_id(hero_id)
        try:
            await self.session.delete(hero)
            await self.session.commit()
        except OperationFailedException:
            await self.session.rollback()
            raise OperationFailedException(f"操作失败")
