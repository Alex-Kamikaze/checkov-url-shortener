from typing import Annotated, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.exc.db_exceptions import URLAlreadyExistsError, URLNotFoundError
from app.services.url_service import URLService

from .deps.url_service_dependency import provide_url_service
from .schemas.url_schema import ShortenedUrlCodeResponseModel, URLShortenerRequestModel, URLPairResponseModel

app = FastAPI(
    title="URL Shortener",
    summary="Сократитель ссылок на самописном алгоритме",
    version="1.0.0",
)
type UrlService = Annotated[URLService, Depends(provide_url_service)]


@app.post(
    "/shorten",
    response_model=ShortenedUrlCodeResponseModel,
    summary="Создание сокращенной ссылки",
    status_code=status.HTTP_201_CREATED,
)
async def create_url_pair(
    original_url: URLShortenerRequestModel, url_service: UrlService
) -> ShortenedUrlCodeResponseModel:
    """
    Создает в базе пару сокращенный URL - Оригинальный URL и возвращает код сокращенного URL
    """
    shortened_url = url_service.create_url_pair(str(original_url.url))
    return ShortenedUrlCodeResponseModel(short_code=shortened_url)

@app.get("/all", summary="Все сокращенные ссылки", status_code=status.HTTP_200_OK, response_model=List[URLPairResponseModel])
async def get_all_url_pairs(url_service: UrlService) -> List[URLPairResponseModel]:
    db_pairs = url_service.get_all_url_pairs_from_db()
    pairs = [URLPairResponseModel(original_url=db_pair.original_url, short_code=db_pair.shortened_url_code) for db_pair in db_pairs]
    return pairs

@app.get(
    "/{code}",
    summary="Переход по сокращенной ссылке",
    status_code=status.HTTP_303_SEE_OTHER,
)
async def redirect_from_short_code(code: str, url_service: UrlService) -> RedirectResponse:
    """
    Ищет в базе оригинальный URL по сокращенному коду и делает ридерект на исходный ресурс
    """
    if code == "all":
        db_pairs = url_service.get_all_url_pairs_from_db()
        pairs = [URLPairResponseModel(original_url=db_pair.original_url, short_code=db_pair.shortened_url_code) for db_pair in db_pairs]
        return pairs
    try:
        original_url = url_service.get_original_url_from_short(code)
        return RedirectResponse(original_url, status_code=303)
    except URLNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Не найдено оригинальной ссылки для данного сокращения!",
        )


@app.delete("/delete-pair/{shorten_url}", summary="Удаление сокращенной ссылки", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url_pair(shorten_url: str, url_service: UrlService):
    """
    Удаляет из базы связку URL
    ### Здесь переиспользуется `URLShortenerRequestModel`, чтобы не дублировать код валидации URL от пользователя
    """

    try:
        url_service.delete_url_pair_from_shorten_url(shorten_url)
    except URLNotFoundError:
        raise HTTPException(status_code=404, detail="URL не найден в базе")