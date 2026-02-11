from typing import ContextManager
from contextlib import nullcontext as does_not_raise

import pytest
from pydantic import ValidationError

from app.api.schemas.url_schema import (
    ShortenedUrlCodeResponseModel,
    URLShortenerRequestModel,
)


@pytest.mark.parametrize(
    ("url", "expectation"),
    [
        ("https://google.com", does_not_raise()),
        ("google.com", pytest.raises(ValidationError))
    ]
)
def test_url_shortener_request_model(url: str, expectation: ContextManager[None | ValidationError]):
    with expectation:
        URLShortenerRequestModel(url=url)  # ty:ignore[invalid-argument-type]

@pytest.mark.parametrize(
    ("code", "expectation"),
    [
        ("hdgtt1273", does_not_raise()),
        ("", pytest.raises(ValidationError)),
        ("t"*22, pytest.raises(ValidationError))
    ]
)
def test_shortened_url_response_schema(code: str, expectation: ContextManager[None | ValidationError]):
    with expectation:
        ShortenedUrlCodeResponseModel(short_code=code)