from typing import Optional
from dataclasses import dataclass
from contextvars import Token
from app.data.repository.repository import Repository

@dataclass
class BaseService:
    """
    Базовый класс для всех сервисов
    
    Attributes:
        repository (Repository): Экземпляр репозитория
        token (Token): Токен для работы с контекстными переменными
    """
    repository: Repository
    token: Optional[Token] = None