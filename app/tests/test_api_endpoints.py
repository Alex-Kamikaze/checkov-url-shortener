from fastapi.testclient import TestClient

def test_endpoint_create_url_pair(test_api_client: TestClient):
    resp = test_api_client.post("/shorten", json={"url": "https://google.com"})
    assert resp.status_code == 201
    assert "short_code" in resp.json().keys()

    error_resp = test_api_client.post("/shorten", json={"url": "https://google.com"})
    assert error_resp.status_code == 400

    error_resp = test_api_client.post("/shorten", json={"url": "ya.ru"}) # Неправильный формат URL
    assert error_resp.status_code == 422

def test_endpoint_make_redirect(test_api_client: TestClient):
    _resp = test_api_client.post("/shorten", json={"url": "https://google.com"})
    assert _resp.status_code == 201
    short_code = _resp.json()["short_code"]

    resp = test_api_client.get(f"/{short_code}", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.has_redirect_location
    assert resp.headers["location"] == "https://google.com/"

    error_resp = test_api_client.get("/INCORRECT_CODE", follow_redirects=False)
    assert error_resp.status_code == 404

def test_endpoint_delete_url_pair(test_api_client: TestClient):
    _resp = test_api_client.post("/shorten", json={"url": "https://google.com"})
    assert _resp.status_code == 201

    resp = test_api_client.request(
        method="DELETE",
        url="/delete-pair",
        json={"url": "https://google.com"}
    ) # Почему разработчики Starlette выпилили аргумент json из метода TestClient.delete()? Загадка...
    assert resp.status_code == 204


    resp = test_api_client.request(
        method="DELETE",
        url="/delete-pair",
        json={"url": "https://ya.com"}
    )
    assert resp.status_code == 404

def test_endpoint_get_all_pairs(test_api_client: TestClient):
    _resp = test_api_client.post("/shorten", json={"url": "https://google.com"})
    assert _resp.status_code == 201

    resp = test_api_client.get("/all")
    assert resp.status_code == 200
    assert len(resp.json()) == 1