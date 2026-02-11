from typing import ContextManager
from contextlib import nullcontext as does_not_raise
import pytest
from app.data.db.models import URLPairModel

@pytest.mark.parametrize(
    ("id", "og_url", "short_url", "expectation"),
    [
        (1, "https://google.com", "tg1f2", does_not_raise()),
        (1, "1vbckbo", "ihsihvs", pytest.raises(ValueError)),
        (1, "https://google.com", "", pytest.raises(ValueError)),
        (1, "https://google.com", "t"*11, pytest.raises(ValueError))
    ]
)
def test_urlpair_model_validation(id: int, og_url: str, short_url: str, expectation: ContextManager[None | ValueError]):
    with expectation:
        URLPairModel(id=id, original_url=og_url, shortened_url_code=short_url) # type: ignore