from typing import Optional, Dict, List
import requests
import json
from loguru import logger
from app.api.schemas.url_schema import URLShortenerRequestModel
from app.data.db.models import URLPairModel
from app.settings import app_settings

class BotService:
    """
    Бизнес-логика для бота
    """

    @staticmethod
    def call_api_for_short_link(url: URLShortenerRequestModel) -> Optional[str]:
        resp = requests.post(f"{app_settings.api_link}/shorten", json={"url": str(url.url)})
        if resp.status_code > 500:
            logger.error(f"Server error: \nStatus Code: {resp.status_code}\nText: {resp.text}")
            return
        
        data: Dict[str, str] = json.loads(resp.text)
        return data.get("short_code")

    @staticmethod
    def call_api_for_all_links() -> List[URLPairModel]:
        resp = requests.get(f"{app_settings.api_link}/all")
        if resp.status_code > 500:
            logger.error(f"Server error: \nStatus Code: {resp.status_code}\nText: {resp.text}")
            return 

        data = json.loads(resp.text)
        return [URLPairModel(original_url=pair.get("original_url"), shortened_url_code=pair.get("short_code")) for pair in data]