import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app

client = TestClient(app)
ver_prefix = "/api/v1"
url = ver_prefix + "/gs/mock"


def test_gs_mock_success():
    payload = {
        "start": "2023-01-01 00:00:00",
        "end": "2023-01-01 01:00:00",
        "delta_minutes": 60,
    }
    response = client.post(url, json=payload)
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert all(isinstance(item, bool) for item in data)


def test_gs_mock_method_not_allowed():
    # technically, we dont need to test this
    # since fastapi will catch this :)
    response = client.get(url)
    assert response.status_code == 422


def test_gs_mock_missing_json():
    # technically, we dont need to test this
    # since fastapi will catch this :)
    response = client.post(url, json={})
    assert response.status_code == 422


def test_gs_mock_invalid_date_format():
    payload = {
        "start": "2023-01-01",
        "end": "hello",
        "delta_minutes": 15,
    }
    response = client.post(url, json=payload)
    assert response.status_code == 422


def test_gs_mock_alternative_date_format():
    payload = {
        "start": "2023-01-01",
        "end": "2023-01-01 01:00:00",
        "delta_minutes": 15,
        "seed": 42,
    }
    response = client.post(url, json=payload)
    expected = [True, False, True, True]
    assert response.status_code == 200
    assert response.json() == expected


def test_gs_mock_missing_parameters():
    # technically, we dont need to test this
    # since fastapi will catch this :)
    payload = {"start": "2023-01-01 00:00:00", "end": "2023-01-01 01:00:00"}
    response = client.post(url, json=payload)
    data = response.json()
    assert response.status_code == 422


def test_response_is_reproducable():
    payload = {
        "start": "2023-01-01 00:00:00",
        "end": "2023-01-01 01:00:00",
        "delta_minutes": 15,
        "seed": 42,
    }
    response1 = client.post(url, json=payload)
    response2 = client.post(url, json=payload)
    assert response1.json() == response2.json()


def test_response_is_not_reproducable():
    payload = {
        "start": "2023-01-01 00:00:00",
        "end": "2023-01-03 01:00:00",
        "delta_minutes": 15,
    }
    response1 = client.post(url, json=payload)
    response2 = client.post(url, json=payload)
    if response1.json() == response2.json():
        response2 = client.post(url, json=payload)
    assert response1.json() != response2.json()
