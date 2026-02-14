from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, PositiveInt


class ApplicationSettings(BaseSettings):
    db_name: str = Field(description="Название базы для подключения")
    port: PositiveInt = Field(description="Порт для работы API")
    host: str = Field(description="Хост, на котором запускается приложение")
    telegram_api_key: Optional[str] = Field(description="Ключ для работы бота сократителя ссылок")
    api_link: Optional[str] = Field(description="API, куда надо отправлять запрос на сокращение ссылки (по логике, это наш APi :) ")
    model_config = SettingsConfigDict(case_sensitive=False, env_file=".env")

    @field_validator("db_name")
    @classmethod
    def validate_db_suffix(cls, value: str) -> str:
        suffix = Path(value).suffix
        if suffix not in (".sqlite3", ".db", ".db3", ".sqlite"):
            raise ValueError(f"Неправильное расширение файла базы данных: {suffix}")

        return value

    @field_validator("api_link", mode="before")
    @classmethod
    def valiate_site_host(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if value.endswith("/"):
                raise ValueError("Ошибка в адресе сайта: уберите / из конца ссылки!")

        return value

app_settings = ApplicationSettings() # ty:ignore[missing-argument]