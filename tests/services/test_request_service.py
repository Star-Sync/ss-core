import numpy as np
import pytest
import datetime
from skyfield.api import EarthSatellite, load
from app.services.request import angle_diff, get_excl_times, is_visible
from app.entities.GroundStation import GroundStation


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
    grounds_stations = {
        "inuvik_northwest": GroundStation(
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

    # Define test time window
    start_time = datetime.datetime(2025, 1, 21, 6, 0)
    end_time = datetime.datetime(2025, 1, 21, 18, 0)

    # Call angle_diff function
    angles = angle_diff(start_time, end_time, sats["scisat"], sats["neossat"], gs_pos)

    # Verify results
    assert isinstance(angles, list)
    assert angles == [
        (
            datetime.datetime(2025, 1, 21, 9, 23, tzinfo=datetime.timezone.utc),
            float(162.24168163454078),
        ),
        (
            datetime.datetime(2025, 1, 21, 9, 24, tzinfo=datetime.timezone.utc),
            float(145.99602825276736),
        ),
        (
            datetime.datetime(2025, 1, 21, 9, 25, tzinfo=datetime.timezone.utc),
            float(127.19194285524681),
        ),
        (
            datetime.datetime(2025, 1, 21, 9, 26, tzinfo=datetime.timezone.utc),
            float(105.79401654478734),
        ),
        (
            datetime.datetime(2025, 1, 21, 9, 27, tzinfo=datetime.timezone.utc),
            float(82.26750378176554),
        ),
        (
            datetime.datetime(2025, 1, 21, 9, 28, tzinfo=datetime.timezone.utc),
            float(57.96793362637979),
        ),
        (
            datetime.datetime(2025, 1, 21, 9, 29, tzinfo=datetime.timezone.utc),
            float(35.15317996160348),
        ),
        (
            datetime.datetime(2025, 1, 21, 9, 30, tzinfo=datetime.timezone.utc),
            float(16.823439375414708),
        ),
        (
            datetime.datetime(2025, 1, 21, 11, 5, tzinfo=datetime.timezone.utc),
            float(85.51354418526253),
        ),
        (
            datetime.datetime(2025, 1, 21, 11, 6, tzinfo=datetime.timezone.utc),
            float(64.15228469001005),
        ),
        (
            datetime.datetime(2025, 1, 21, 11, 7, tzinfo=datetime.timezone.utc),
            float(45.23010954818406),
        ),
        (
            datetime.datetime(2025, 1, 21, 11, 8, tzinfo=datetime.timezone.utc),
            float(28.133699761044344),
        ),
        (
            datetime.datetime(2025, 1, 21, 11, 9, tzinfo=datetime.timezone.utc),
            float(12.57070594730534),
        ),
        (
            datetime.datetime(2025, 1, 21, 11, 10, tzinfo=datetime.timezone.utc),
            float(3.892896682384997),
        ),
        (
            datetime.datetime(2025, 1, 21, 12, 47, tzinfo=datetime.timezone.utc),
            float(12.603949109610594),
        ),
        (
            datetime.datetime(2025, 1, 21, 12, 48, tzinfo=datetime.timezone.utc),
            float(7.047809271260551),
        ),
        (
            datetime.datetime(2025, 1, 21, 12, 49, tzinfo=datetime.timezone.utc),
            float(10.985794951083049),
        ),
        (
            datetime.datetime(2025, 1, 21, 14, 27, tzinfo=datetime.timezone.utc),
            float(22.804273810306654),
        ),
        (
            datetime.datetime(2025, 1, 21, 14, 28, tzinfo=datetime.timezone.utc),
            float(22.791053455380585),
        ),
    ]
    if angles:
        for time, angle in angles:
            assert isinstance(time, datetime.datetime)
            assert isinstance(angle, float)
            assert 0 <= angle <= 180  # Angle should be between 0 and 180 degrees


def test_get_excl_times(setup_satellites, setup_ground_station):
    # Get the fixtures
    sats = setup_satellites
    gs_pos = setup_ground_station["prince_albert"].get_sf_geo_position()

    # Define test time window
    start_time = datetime.datetime(2025, 1, 21, 6, 0)
    end_time = datetime.datetime(2025, 1, 21, 18, 0)

    # Call angle_diff function
    angles = angle_diff(start_time, end_time, sats["scisat"], sats["neossat"], gs_pos)

    # Test different exclusion angles
    for excl_angle in [10]:
        # Call get_excl_times function
        exclusion_times = get_excl_times(angles, excl_angle)

        # Verify results
        assert isinstance(exclusion_times, list)
        assert exclusion_times == [
            (
                datetime.datetime(2025, 1, 21, 11, 10, tzinfo=datetime.timezone.utc),
                datetime.datetime(2025, 1, 21, 11, 10, tzinfo=datetime.timezone.utc),
            ),
            (
                datetime.datetime(2025, 1, 21, 12, 48, tzinfo=datetime.timezone.utc),
                datetime.datetime(2025, 1, 21, 12, 48, tzinfo=datetime.timezone.utc),
            ),
        ]
        # Check if each exclusion time pair is valid
        for start, end in exclusion_times:
            assert isinstance(start, datetime.datetime)
            assert isinstance(end, datetime.datetime)
            assert start <= end


def test_is_visible(setup_satellites, setup_ground_station):
    # Get the fixtures
    sats = setup_satellites
    gs = setup_ground_station["prince_albert"]

    # Define test time
    time = datetime.datetime(2025, 1, 21, 6, 0, tzinfo=datetime.timezone.utc)

    # Call is_visible function
    visible = is_visible(sats["scisat"], gs, time)

    # Verify results
    assert isinstance(visible, np.bool)
    assert visible == False
