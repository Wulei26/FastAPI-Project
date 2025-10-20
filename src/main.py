from fastapi import FastAPI, Response, Request, Depends
from core.config import app_settings
from core.lifespan import lifespan

from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db
from app import models  # 导入所有模型以确保它们被注册
from core.exceptions import global_exception_handler

"""
USE lifespan state instated of app.state
"""

app = FastAPI(
    title=app_settings.app_name,
    description=f"{app_settings.app_name}接口文档",
    version=app_settings.app_version,
    lifespan=lifespan,
)
app.add_exception_handler(Exception, global_exception_handler)


# 路由引入
@app.get("/")
def read_root(
    # 使用 FastAPI 的依赖注入系统来获取配置实例
    # FastAPI 会自动调用 get_settings()，由于缓存的存在，这几乎没有开销
):
    """
    一个示例端点，演示如何访问配置。
    """
    return {
        "message": f"Hello from the {app_settings.app_name}!",
        # 演示如何使用在模型中动态计算的属性
        "database_url": app_settings.app_host,
        "jwt_secret": app_settings.app_root_path,
    }


@app.get("/health")
async def health_check(request: Request, response: Response):
    print(request)
    response.status_code = 200
    print(response)
    return {"status": "ok 👍 "}


@app.get("/db-check")
async def db_check(db: AsyncSession = Depends(get_db)):
    """
    一个简单的端点，用于检查数据库连接是否正常工作。
    """
    try:
        # 执行一个简单的查询来验证连接
        result = await db.execute(text("SELECT 1"))
        if result.scalar_one() == 1:
            return {"status": "ok", "message": "数据库连接成功！"}
    except Exception as e:
        return {"status": "error", "message": f"数据库连接失败: {e}"}
