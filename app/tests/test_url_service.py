from contextlib import nullcontext as does_not_raise
import pytest
from app.services.url_service import URLService
from app.data.db.models import URLPairModel
from app.exc.db_exceptions import URLAlreadyExistsError, URLNotFoundError
from app.exc.url_exceptions import IncorrectURLSuppliedError

def test_service_generate_short_url(mock_url_service: URLService):
    """
    Проверяем алгоритм генерации сокращенных ссылок
    """

    initial_site = "https://google.com"
    short_url = mock_url_service._create_short_url(initial_site)

    same_short_url = mock_url_service._create_short_url(initial_site) # Тестируем идемпотентность метода генерации сокращений URL'ов
    
    assert short_url == same_short_url

def test_service_url_pair_fabric(mock_url_service: URLService):
    """
    Проверяем создание пар связанных URL'ов
    """

    initial_site = "https://google.com/"
    pair = mock_url_service._initialize_url_pair_model(initial_site)
    shorten_url = mock_url_service._create_short_url(initial_site)
    
    assert type(pair) is URLPairModel
    assert str(pair.original_url) == initial_site
    assert pair.shortened_url_code == shorten_url

def test_service_insert_pair_in_database(mock_url_service: URLService):
     initial_site = "https://google.com/"
     pair = mock_url_service._initialize_url_pair_model(initial_site)
     mock_url_service._insert_url_pair_in_database(pair)


def test_service_client_method_for_creating_url_pair(mock_url_service: URLService):
    short_url = mock_url_service.create_url_pair("https://google.com")
    generated_url = mock_url_service._create_short_url("https://google.com")

    assert short_url == generated_url

def test_service_client_method_get_og_url_from_short(mock_url_service: URLService):
    short_code = mock_url_service.create_url_pair("https://google.com")
    found_url = mock_url_service.get_original_url_from_short(short_code)

    assert found_url == "https://google.com/"

    with pytest.raises(URLNotFoundError):
        mock_url_service.get_original_url_from_short("NON_EXISTING")

def test_url_service_delete_pair_with_shorten(mock_url_service: URLService):
    short_url = mock_url_service.create_url_pair("https://google.com")
    with does_not_raise():
        mock_url_service.delete_url_pair_from_shorten_url(short_url)
    
    with pytest.raises(URLNotFoundError):
        mock_url_service.delete_url_pair_from_shorten_url("NON_EXIST")

def test_service_give_all_pairs(mock_url_service: URLService):
    mock_url_service.create_url_pair("https://google.com")
    mock_url_service.create_url_pair("https://ya.ru")

    pairs = mock_url_service.get_all_url_pairs_from_db()
    assert len(pairs) == 2