from contextlib import nullcontext as does_not_raise

import pytest

from app.data.db.models import URLPairModel
from app.data.repository.repository import Repository
from app.exc.db_exceptions import URLAlreadyExistsError


def test_repository_insert_urlpair(mock_repository: Repository):
    pair: URLPairModel = URLPairModel(original_url="https://google.com", shortened_url_code="tfg1")  # ty:ignore[invalid-argument-type]
    with does_not_raise():
        mock_repository.insert_new_url_pair(pair)

    with pytest.raises(URLAlreadyExistsError):
        mock_repository.insert_new_url_pair(pair)

def test_repository_get_original_url_from_shortened(mock_repository: Repository):
     pair: URLPairModel = URLPairModel(original_url="https://google.com", shortened_url_code="tfg1")  # ty:ignore[invalid-argument-type]
     mock_repository.insert_new_url_pair(pair)

     og_url = mock_repository.get_original_url_from_shortened(pair.shortened_url_code)
     assert og_url is not None
     assert og_url == str(pair.original_url)

def test_repository_get_all_pairs(mock_repository: Repository):
     pair: URLPairModel = URLPairModel(original_url="https://google.com", shortened_url_code="tfg1")  # ty:ignore[invalid-argument-type]
     pair_2: URLPairModel = URLPairModel(original_url="https://ya.ru", shortened_url_code="tfg2")  # ty:ignore[invalid-argument-type]
     mock_repository.insert_new_url_pair(pair)
     mock_repository.insert_new_url_pair(pair_2)

     pairs = mock_repository.get_all_pairs()
     assert len(pairs) == 2