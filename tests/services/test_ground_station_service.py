import pytest
from unittest.mock import MagicMock
from app.services.ground_station import GroundStationService
from app.models.ground_station import GroundStationModel, GroundStationCreateModel
from app.entities.GroundStation import GroundStation

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

_gs_create_data = _gs_data.copy()
_gs_create_data.pop("id")


@pytest.fixture
def db_session():
    return MagicMock()


def test_create_ground_station(db_session):
    ground_station_model = GroundStationCreateModel(**_gs_create_data)

    result = GroundStationService.create_ground_station(
        db_session, ground_station_model
    )

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()
    print(result)
    # assert result.id == _gs_data["id"] <--- Needs to be fixed later on
    assert result.name == _gs_data["name"]


def test_update_ground_station_not_found(db_session):
    updated_data = _gs_data.copy()
    updated_data["name"] = "Updated Station"
    ground_station_model = GroundStationModel(**updated_data)

    db_session.query.return_value.filter.return_value.first.return_value = None

    result = GroundStationService.update_ground_station(
        db_session, ground_station_model
    )

    db_session.query.assert_called_once_with(GroundStation)
    db_session.query.return_value.filter.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()
    assert result.id == 1
    assert result.name == "Updated Station"


def test_get_ground_stations(db_session):
    ground_station = GroundStation(**_gs_data)
    db_session.query.return_value.all.return_value = [ground_station]

    result = GroundStationService.get_ground_stations(db_session)

    db_session.query.assert_called_once_with(GroundStation)
    assert len(result) == 1
    assert result[0].name == "Test Station"


def test_get_ground_station(db_session):
    ground_station = GroundStation(**_gs_data)
    db_session.query.return_value.filter.return_value.first.return_value = (
        ground_station
    )

    result = GroundStationService.get_ground_station(db_session, 1)

    db_session.query.assert_called_once_with(GroundStation)
    db_session.query.return_value.filter.assert_called_once()
    assert result.name == "Test Station"


def test_delete_ground_station(db_session):
    ground_station = GroundStation(**_gs_data)
    db_session.query.return_value.filter.return_value.first.return_value = (
        ground_station
    )

    result = GroundStationService.delete_ground_station(db_session, 1)

    db_session.query.assert_called_once_with(GroundStation)
    db_session.query.return_value.filter.assert_called_once()
    db_session.delete.assert_called_once_with(ground_station)
    db_session.commit.assert_called_once()
    assert result is True


def test_delete_ground_station_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    result = GroundStationService.delete_ground_station(db_session, 1)

    db_session.query.assert_called_once_with(GroundStation)
    db_session.query.return_value.filter.assert_called_once()
    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()
    assert result is False
