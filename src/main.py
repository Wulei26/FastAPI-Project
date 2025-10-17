from fastapi import FastAPI, Response
from core.config import app_settings

app = FastAPI(
    title=app_settings.app_name,
    description=f"{app_settings.app_name}接口文档",
    version=app_settings.app_version,
    # lifespan=lifespan,
)
# src/main.py

# app = FastAPI(description="FastAPI 练习项目实战")


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
async def health_check(response: Response):
    response.status_code = 200
    return {"status": "ok 👍 "}
