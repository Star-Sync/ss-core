import numpy as np
import pytest
from datetime import datetime, timedelta, timezone
from skyfield.api import EarthSatellite, load
from app.services.request import angle_diff, get_excl_times, is_visible
from app.entities.GroundStation import GroundStation
from uuid import UUID, uuid4
from sqlmodel import Session, SQLModel, create_engine
from app.services.request import RequestService
from app.models.request import RFTimeRequestModel, ContactRequestModel
from app.entities.Request import RFRequest, ContactRequest
from app.entities.Satellite import Satellite


@pytest.fixture(name="db")
def db_fixture():
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture
def setup_satellites():
    # Define TLEs for test satellites
    tle_scisat = """SCISAT 1
1 27858U 03036A   24271.51787419  .00002340  00000+0  31635-3 0  9999
2 27858  73.9336 337.0907 0007403 194.1129 165.9841 14.79656508138550"""

    tle_neossat = """NEOSSAT
1 39089U 13009D   24271.52543360  .00000662  00000+0  24595-3 0  9997
2 39089  98.4054  96.2203 0010420 322.4732  37.5725 14.35304192606691"""

    ts = load.timescale()
    scisat = EarthSatellite(
        tle_scisat.splitlines()[1],
        tle_scisat.splitlines()[2],
        tle_scisat.splitlines()[0],
    )
    neossat = EarthSatellite(
        tle_neossat.splitlines()[1],
        tle_neossat.splitlines()[2],
        tle_neossat.splitlines()[0],
    )

    return {"scisat": scisat, "neossat": neossat, "ts": ts}


@pytest.fixture
def setup_ground_station():
    # we have to set the id manually here because the service usually sets it, but
    # we dont have a db session here and the id is set by the db
    grounds_stations = {
        "inuvik_northwest": GroundStation(
            id=1,
            name="Inuvik NorthWest",
            lat=68.3195,
            lon=-133.549,
            height=102.5,
            mask=0,
            uplink=0,
            downlink=0,
            science=0,
        ),
        "prince_albert": GroundStation(
            id=2,
            name="Prince Albert",
            lat=53.2124,
            lon=-105.934,
            height=490.3,
            mask=0,
            uplink=0,
            downlink=0,
            science=0,
        ),
        "gatineau_quebec": GroundStation(
            id=3,
            name="Gatineau Quebec",
            lat=45.5846,
            lon=-75.8083,
            height=240.1,
            mask=0,
            uplink=0,
            downlink=0,
            science=0,
        ),
    }
    return grounds_stations


def test_angle_diff(setup_satellites, setup_ground_station):
    # Get the fixtures
    sats = setup_satellites
    gs_pos = setup_ground_station["prince_albert"].get_sf_geo_position()

    # Define test time window with UTC timezone
    start_time = datetime(2025, 1, 21, 6, 0, tzinfo=timezone.utc)
    end_time = datetime(2025, 1, 21, 18, 0, tzinfo=timezone.utc)

    # Call angle_diff function
    angles = angle_diff(start_time, end_time, sats["scisat"], sats["neossat"], gs_pos)

    # Verify results
    assert isinstance(angles, list)
    # Update expected values with UTC timezone
    expected_angles = [
        (datetime(2025, 1, 21, 9, 23, tzinfo=timezone.utc), float(162.24168163454078)),
        (datetime(2025, 1, 21, 9, 24, tzinfo=timezone.utc), float(145.99602825276736)),
        (datetime(2025, 1, 21, 9, 25, tzinfo=timezone.utc), float(127.19194285524681)),
        (datetime(2025, 1, 21, 9, 26, tzinfo=timezone.utc), float(105.79401654478734)),
        (datetime(2025, 1, 21, 9, 27, tzinfo=timezone.utc), float(82.26750378176554)),
        (datetime(2025, 1, 21, 9, 28, tzinfo=timezone.utc), float(57.96793362637979)),
        (datetime(2025, 1, 21, 9, 29, tzinfo=timezone.utc), float(35.15317996160348)),
        (datetime(2025, 1, 21, 9, 30, tzinfo=timezone.utc), float(16.823439375414708)),
        (datetime(2025, 1, 21, 11, 5, tzinfo=timezone.utc), float(85.51354418526253)),
        (datetime(2025, 1, 21, 11, 6, tzinfo=timezone.utc), float(64.15228469001005)),
        (datetime(2025, 1, 21, 11, 7, tzinfo=timezone.utc), float(45.23010954818406)),
        (datetime(2025, 1, 21, 11, 8, tzinfo=timezone.utc), float(28.133699761044344)),
        (datetime(2025, 1, 21, 11, 9, tzinfo=timezone.utc), float(12.57070594730534)),
        (datetime(2025, 1, 21, 11, 10, tzinfo=timezone.utc), float(3.892896682384997)),
        (datetime(2025, 1, 21, 12, 47, tzinfo=timezone.utc), float(12.603949109610594)),
        (datetime(2025, 1, 21, 12, 48, tzinfo=timezone.utc), float(7.047809271260551)),
        (datetime(2025, 1, 21, 12, 49, tzinfo=timezone.utc), float(10.985794951083049)),
        (datetime(2025, 1, 21, 14, 27, tzinfo=timezone.utc), float(22.804273810306654)),
        (datetime(2025, 1, 21, 14, 28, tzinfo=timezone.utc), float(22.791053455380585)),
    ]

    if angles:
        for time, angle in angles:
            assert isinstance(time, datetime)
            assert isinstance(angle, float)
            assert 0 <= angle <= 180  # Angle should be between 0 and 180 degrees

    assert angles == expected_angles


def test_get_excl_times(setup_satellites, setup_ground_station):
    # Get the fixtures
    sats = setup_satellites
    gs_pos = setup_ground_station["prince_albert"].get_sf_geo_position()

    # Define test time window with UTC timezone
    start_time = datetime(2025, 1, 21, 6, 0, tzinfo=timezone.utc)
    end_time = datetime(2025, 1, 21, 18, 0, tzinfo=timezone.utc)

    # Call angle_diff function
    angles = angle_diff(start_time, end_time, sats["scisat"], sats["neossat"], gs_pos)

    # Test different exclusion angles
    for excl_angle in [10]:
        # Call get_excl_times function
        exclusion_times = get_excl_times(angles, excl_angle)

        # Verify results
        assert isinstance(exclusion_times, list)
        expected_times = [
            (
                datetime(2025, 1, 21, 11, 10, tzinfo=timezone.utc),
                datetime(2025, 1, 21, 11, 10, tzinfo=timezone.utc),
            ),
            (
                datetime(2025, 1, 21, 12, 48, tzinfo=timezone.utc),
                datetime(2025, 1, 21, 12, 48, tzinfo=timezone.utc),
            ),
        ]
        assert exclusion_times == expected_times

        # Check if each exclusion time pair is valid
        for start, end in exclusion_times:
            assert isinstance(start, datetime)
            assert isinstance(end, datetime)
            assert start <= end


def test_is_visible(setup_satellites, setup_ground_station):
    # Get the fixtures
    sats = setup_satellites
    gs = setup_ground_station["prince_albert"]

    # Define test time with UTC timezone
    time = datetime(2025, 1, 21, 6, 0, tzinfo=timezone.utc)

    # Call is_visible function
    visible = is_visible(sats["scisat"], gs, time)

    # Verify results
    assert isinstance(visible, np.bool_)
    assert visible == False


@pytest.fixture
def sample_satellite(db: Session):
    satellite = Satellite(
        name="SCISAT-1",
        tle="1 27858U 03036A   24271.51787419  .00002340  00000+0  31635-3 0  9999\n2 27858  73.9336 337.0907 0007403 194.1129 165.9841 14.79656508138550",
    )
    db.add(satellite)
    db.commit()
    db.refresh(satellite)
    return satellite


@pytest.fixture
def sample_ground_station(db: Session):
    station = GroundStation(
        id=1,
        name="Inuvik",
        lat=68.3195,
        lon=-133.549,
        height=102.5,
        mask=5,
        uplink=True,
        downlink=True,
        science=True,
    )
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


@pytest.fixture
def sample_rf_request_model(sample_satellite):
    current_time = datetime.now()
    return RFTimeRequestModel(
        missionName="Test Mission",
        satelliteId=sample_satellite.id,
        startTime=current_time + timedelta(hours=1),
        endTime=current_time + timedelta(hours=2),
        uplinkTime=600,
        downlinkTime=600,
        scienceTime=300,
        minimumNumberOfPasses=2,
    )


@pytest.fixture
def sample_contact_request_model(sample_satellite):
    current_time = datetime.now()
    start_time = current_time + timedelta(hours=1)
    end_time = start_time + timedelta(minutes=30)
    return ContactRequestModel(
        missionName="Test Mission",
        satelliteId=sample_satellite.id,
        station_id=1,
        orbit=0,
        uplink=True,
        telemetry=True,
        science=False,
        aosTime=start_time,
        rfOnTime=start_time + timedelta(minutes=2),
        rfOffTime=end_time - timedelta(minutes=2),
        losTime=end_time,
    )


def test_create_rf_request(db: Session, sample_rf_request_model):
    # Create RF request
    rf_request = RequestService.create_rf_request(db, sample_rf_request_model)

    # Verify the request was created with correct values
    assert rf_request.mission == sample_rf_request_model.missionName
    assert rf_request.satellite_id == sample_rf_request_model.satelliteId
    assert rf_request.start_time == sample_rf_request_model.startTime
    assert rf_request.end_time == sample_rf_request_model.endTime
    assert rf_request.uplink_time_requested == int(sample_rf_request_model.uplinkTime)
    assert rf_request.downlink_time_requested == int(
        sample_rf_request_model.downlinkTime
    )
    assert rf_request.science_time_requested == int(sample_rf_request_model.scienceTime)
    assert rf_request.min_passes == sample_rf_request_model.minimumNumberOfPasses
    assert not rf_request.scheduled
    assert rf_request.ground_station_id is None


def test_create_contact_request(db: Session, sample_contact_request_model):
    # Create contact request
    contact_request = RequestService.create_contact_request(
        db, sample_contact_request_model
    )

    # Verify the request was created with correct values
    assert contact_request.mission == sample_contact_request_model.missionName
    assert contact_request.satellite_id == sample_contact_request_model.satelliteId
    assert contact_request.start_time == sample_contact_request_model.aosTime
    assert contact_request.end_time == sample_contact_request_model.losTime
    assert contact_request.uplink == sample_contact_request_model.uplink
    assert contact_request.telemetry == sample_contact_request_model.telemetry
    assert contact_request.science == sample_contact_request_model.science
    assert contact_request.aos == sample_contact_request_model.aosTime
    assert contact_request.los == sample_contact_request_model.losTime
    assert contact_request.rf_on == sample_contact_request_model.rfOnTime
    assert contact_request.rf_off == sample_contact_request_model.rfOffTime
    assert not contact_request.scheduled
    assert contact_request.ground_station_id == sample_contact_request_model.station_id


def test_get_rf_time_request(db: Session, sample_rf_request_model):
    # Create RF request
    created_request = RequestService.create_rf_request(db, sample_rf_request_model)

    # Get the request
    retrieved_request = RequestService.get_rf_time_request(db, created_request.id)

    # Verify the request was retrieved correctly
    assert retrieved_request is not None
    assert retrieved_request.id == created_request.id
    assert retrieved_request.mission == created_request.mission


def test_get_contact_request(db: Session, sample_contact_request_model):
    # Create contact request
    created_request = RequestService.create_contact_request(
        db, sample_contact_request_model
    )

    # Get the request
    retrieved_request = RequestService.get_contact_request(db, created_request.id)

    # Verify the request was retrieved correctly
    assert retrieved_request is not None


def test_delete_rf_time_request(db: Session, sample_rf_request_model):
    # Create RF request
    created_request = RequestService.create_rf_request(db, sample_rf_request_model)

    # Delete the request
    RequestService.delete_rf_time_request(db, created_request.id)

    # Verify the request was deleted
    retrieved_request = RequestService.get_rf_time_request(db, created_request.id)
    assert retrieved_request is None


def test_delete_contact_request(db: Session, sample_contact_request_model):
    # Create contact request
    created_request = RequestService.create_contact_request(
        db, sample_contact_request_model
    )

    # Delete the request
    RequestService.delete_contact_request(db, created_request.id)

    # Verify the request was deleted
    retrieved_request = RequestService.get_contact_request(db, created_request.id)
    assert retrieved_request is None


def test_get_all_requests(
    db: Session, sample_rf_request_model, sample_contact_request_model
):
    # Create both types of requests
    rf_request = RequestService.create_rf_request(db, sample_rf_request_model)
    contact_request = RequestService.create_contact_request(
        db, sample_contact_request_model
    )

    # Get all requests
    all_requests = RequestService.get_all_requests(db)

    # Verify both requests are returned
    assert len(all_requests) == 2
    request_ids = {str(req.id) for req in all_requests}
    assert str(rf_request.id) in request_ids
    assert str(contact_request.id) in request_ids


def test_transform_request_to_general(
    db: Session, sample_rf_request_model, sample_satellite
):
    # Create RF request
    rf_request = RequestService.create_rf_request(db, sample_rf_request_model)

    # Transform to general model
    general_model = RequestService.transform_request_to_general(db, rf_request)

    # Verify transformation
    assert general_model is not None
    assert general_model.requestType == "RFTime"
    assert general_model.mission == rf_request.mission
    assert general_model.satellite_name == sample_satellite.name
    assert general_model.startTime == rf_request.start_time
    assert general_model.endTime == rf_request.end_time


def test_nonexistent_request(db: Session):
    # Try to get a request with a non-existent ID
    nonexistent_id = uuid4()
    rf_request = RequestService.get_rf_time_request(db, nonexistent_id)
    contact_request = RequestService.get_contact_request(db, nonexistent_id)

    # Verify both are None
    assert rf_request is None
    assert contact_request is None


def test_invalid_request_data(db: Session, sample_satellite):
    current_time = datetime.now(timezone.utc)
    # Create an RF request model with invalid data
    invalid_rf_model = RFTimeRequestModel(
        missionName="",  # Empty mission name
        satelliteId=sample_satellite.id,
        startTime=current_time - timedelta(hours=2),  # End time before start time
        endTime=current_time - timedelta(hours=1),
        uplinkTime=-1,  # Negative time
        downlinkTime=0,
        scienceTime=0,
        minimumNumberOfPasses=0,  # Invalid number of passes
    )

    # Verify creation fails with ValueError
    with pytest.raises(ValueError):
        RequestService.create_rf_request(db, invalid_rf_model)
