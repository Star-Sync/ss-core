# type: ignore
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.models.ground_station import GroundStationModel
from app.main import app
from app.services.db import get_db
from app.services.ground_station import GroundStationService


@pytest.fixture(name="mock_db")
def session_fixture():
    mock_db = MagicMock()
    yield mock_db


@pytest.fixture(name="client")
def client_fixture(mock_db: MagicMock):
    def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_mocks(mock_db: MagicMock):
    """
    Reset the mock database before each test to prevent side effects
    """
    mock_db.reset_mock()
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)


_ver_prefix = "/api/v1"

_gs_data = {
    "id": 1,
    "name": "Test Station",
    "lat": 68.3,
    "lon": 133.5,
    "height": 100.0,
    "mask": 5,
    "uplink": 50,
    "downlink": 100,
    "science": 100,
}

_mock_db_response = GroundStationModel(**_gs_data)


def test_create_ground_station(client: TestClient):
    with patch.object(
        GroundStationService, "create_ground_station", return_value=_mock_db_response
    ):
        response = client.post(f"{_ver_prefix}/gs", json=_gs_data)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Test Station"
    assert data["lat"] == 68.3
    assert data["lon"] == 133.5
    assert data["height"] == 100.0
    assert data["mask"] == 5
    assert data["uplink"] == 50
    assert data["downlink"] == 100
    assert data["science"] == 100


def test_update_ground_station(client: TestClient):
    mock_db_response = GroundStationModel(**_gs_data)

    with patch.object(
        GroundStationService, "update_ground_station", return_value=mock_db_response
    ):
        response = client.post(f"{_ver_prefix}/gs", json=_gs_data)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test Station"
    assert data["lat"] == 68.3
    assert data["lon"] == 133.5
    assert data["height"] == 100.0
    assert data["mask"] == 5
    assert data["uplink"] == 50
    assert data["downlink"] == 100
    assert data["science"] == 100


def test_create_ground_station_invalid_json(client: TestClient):
    invalid_data = _gs_data.copy()
    invalid_data.pop("mask")

    response = client.post(f"{_ver_prefix}/gs", json=invalid_data)

    assert response.status_code == 422
    assert "detail" in response.json()


def test_get_ground_stations(client: TestClient):
    with patch.object(
        GroundStationService, "get_ground_stations", return_value=[_mock_db_response]
    ):
        response = client.get(f"{_ver_prefix}/gs")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_ground_station(client: TestClient):
    gs_id = 1

    with patch.object(
        GroundStationService, "get_ground_station", return_value=_mock_db_response
    ):
        response = client.get(f"{_ver_prefix}/gs/{gs_id}")

    assert response.status_code == 200
    assert response.json()["id"] == gs_id


def test_get_ground_station_not_found(client: TestClient):
    with patch.object(GroundStationService, "get_ground_station", return_value=None):
        response = client.get(f"{_ver_prefix}/gs/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Ground station not found"}


def test_delete_ground_station(client: TestClient):
    gs_id = 1

    with patch.object(GroundStationService, "delete_ground_station", return_value=True):
        response = client.delete(f"{_ver_prefix}/gs/{gs_id}")

    assert response.status_code == 200
    assert response.json() == {"detail": "Ground station deleted successfully"}


def test_delete_ground_station_not_found(client: TestClient):
    with patch.object(
        GroundStationService, "delete_ground_station", return_value=False
    ):
        response = client.delete(f"{_ver_prefix}/gs/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Ground station not found"}
