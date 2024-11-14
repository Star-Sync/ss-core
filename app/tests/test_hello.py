from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
ver_prefix = "/api/v1"
url = ver_prefix + "/hello"


def test_hello():
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
