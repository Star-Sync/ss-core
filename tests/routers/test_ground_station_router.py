from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.models.ground_station import GroundStationModel, GroundStationCreateModel
from app.main import app
from app.services.db import get_db
from app.services.ground_station import GroundStationService

mock_db = MagicMock()


def override_get_db():
    yield mock_db


app.dependency_overrides[get_db] = override_get_db

_client = TestClient(app)
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


@pytest.fixture(autouse=True)
def reset_mocks():
    """
    Reset the mock database before each test to prevent side effects
    """
    mock_db.reset_mock()
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)


def test_create_ground_station():
    mock_db_response = GroundStationModel(**_gs_data)

    with patch.object(
        GroundStationService, "create_ground_station", return_value=mock_db_response
    ):
        response = _client.post(_ver_prefix + "/gs", json=_gs_data)

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


def test_update_ground_station():
    mock_db_response = GroundStationModel(**_gs_data)

    with patch.object(
        GroundStationService, "update_ground_station", return_value=mock_db_response
    ):
        response = _client.post(_ver_prefix + "/gs", json=_gs_data)

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


def test_create_ground_station_invalid_json():
    invalid_data = _gs_data.copy()
    invalid_data.pop("mask")

    response = _client.post(_ver_prefix + "/gs", json=invalid_data)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_get_ground_stations():
    mock_db_response = GroundStationModel(**_gs_data)

    with patch.object(
        GroundStationService, "get_ground_stations", return_value=[mock_db_response]
    ):
        response = _client.get(_ver_prefix + "/gs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_ground_station():
    mock_db_response = GroundStationModel(**_gs_data)
    gs_id = 1

    with patch.object(
        GroundStationService, "get_ground_station", return_value=mock_db_response
    ):
        response = _client.get(_ver_prefix + f"/gs/{gs_id}")
    assert response.status_code == 200
    assert response.json()["id"] == gs_id


def test_get_ground_station_not_found():
    with patch.object(GroundStationService, "get_ground_station", return_value=None):
        response = _client.get(_ver_prefix + f"/gs/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Ground station not found"}


def test_delete_ground_station():
    gs_id = 1

    with patch.object(GroundStationService, "delete_ground_station", return_value=True):
        response = _client.delete(_ver_prefix + f"/gs/{gs_id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "Ground station deleted successfully"}


def test_delete_ground_station_not_found():
    with patch.object(
        GroundStationService, "delete_ground_station", return_value=False
    ):
        response = _client.delete(_ver_prefix + "/gs/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Ground station not found"}
