import uvicorn
from core.config import app_settings

from main import app

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=app_settings.app_host,
        port=app_settings.app_port,
        reload=app_settings.app_reload,
    )
