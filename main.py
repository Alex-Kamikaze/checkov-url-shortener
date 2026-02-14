import uvicorn
from loguru import logger
from app.api.views import app
from app.settings import app_settings

if __name__ == "__main__":
    logger.info(f"Starting up API on host {app_settings.host}, port {app_settings.port}")
    uvicorn.run(app=app, port=app_settings.port, host=str(app_settings.host))