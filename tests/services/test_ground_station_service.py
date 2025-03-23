import pytest
from app.entities.Satellite import Satellite
from app.entities.ExclusionCone import ExclusionCone
from app.entities.GroundStation import GroundStation
from app.services.ground_station import GroundStationService
from app.models.ground_station import (
    GroundStationModel,
    GroundStationCreateModel,
    GroundStationUpdateModel,
)
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

_gs_model = GroundStationModel(
    id=1,
    name="Test Station",
    lat=68.3,
    lon=133.5,
    height=100.0,
    mask=5,
    uplink=50,
    downlink=100,
    science=100,
)
_gs_create_model = GroundStationCreateModel(**_gs_model.model_dump())


@pytest.fixture(name="db_session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(
        engine,
        tables=[Satellite.__table__, ExclusionCone.__table__, GroundStation.__table__],  # type: ignore
    )
    with Session(engine) as session:
        yield session


def test_create_ground_station(db_session: Session):
    result = GroundStationService.create_ground_station(db_session, _gs_create_model)

    assert result.id == 1
    assert result.name == "Test Station"
    assert result.lat == 68.3
    assert result.lon == 133.5
    assert result.height == 100.0
    assert result.mask == 5
    assert result.uplink == 50
    assert result.downlink == 100
    assert result.science == 100


def test_update_ground_station(db_session: Session):
    GroundStationService.create_ground_station(db_session, _gs_create_model)

    gs_id = _gs_model.id
    updated_gs_model = GroundStationUpdateModel(**_gs_model.model_dump())
    updated_gs_model.name = "Updated Station"
    updated_gs_model.uplink = 100

    result = GroundStationService.update_ground_station(
        db_session, gs_id, updated_gs_model
    )

    assert result.id == 1
    assert result.name == "Updated Station"  # Updated value
    assert result.lat == 68.3
    assert result.lon == 133.5
    assert result.height == 100.0
    assert result.mask == 5
    assert result.uplink == 100  # Updated value
    assert result.downlink == 100
    assert result.science == 100


def test_update_ground_station_not_found(db_session: Session):
    GroundStationService.create_ground_station(db_session, _gs_create_model)

    gs_id = 2  # ID that does not exist
    updated_gs_model = GroundStationUpdateModel(**_gs_model.model_dump())
    updated_gs_model.name = "Updated Station"

    with pytest.raises(Exception) as e:
        GroundStationService.update_ground_station(db_session, gs_id, updated_gs_model)
    assert "Ground Station with ID 2 not found" in str(e.value)


def test_get_ground_stations(db_session: Session):
    GroundStationService.create_ground_station(db_session, _gs_create_model)
    GroundStationService.create_ground_station(db_session, _gs_create_model)

    result = GroundStationService.get_ground_stations(db_session)

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2


def test_get_ground_station(db_session: Session):
    GroundStationService.create_ground_station(db_session, _gs_create_model)

    result = GroundStationService.get_ground_station(db_session, 1)

    assert result is not None
    assert result.id == 1
    assert result.name == "Test Station"
    assert result.lat == 68.3
    assert result.lon == 133.5
    assert result.height == 100.0
    assert result.mask == 5
    assert result.uplink == 50
    assert result.downlink == 100
    assert result.science == 100


def test_delete_ground_station(db_session: Session):
    GroundStationService.create_ground_station(db_session, _gs_create_model)

    result = GroundStationService.delete_ground_station(db_session, 1)

    assert result is True


def test_delete_ground_station_not_found(db_session: Session):
    GroundStationService.create_ground_station(db_session, _gs_create_model)

    result = GroundStationService.delete_ground_station(db_session, 2)

    assert result is False
