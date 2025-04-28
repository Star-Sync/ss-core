import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.services.station_sim import StationSimulatorService
from fastapi import HTTPException


@pytest.fixture
def station_sim_service():
    return StationSimulatorService()


@pytest.fixture
def mock_schedule_response():
    mock = MagicMock()
    mock.json.return_value = {"status": "success"}
    return mock


@pytest.fixture
def mock_state_response():
    mock = MagicMock()
    mock.json.return_value = {"status": "success"}
    return mock


@pytest.fixture
def mock_busy_times_response():
    mock = MagicMock()
    mock.json.return_value = [
        {
            "start_time": "2024-01-01T00:00:00",
            "end_time": "2024-01-01T01:00:00",
            "state": "both_busy",
            "mission": "SCISAT"
        }
    ]
    return mock


def test_schedule_pass_success(station_sim_service, mock_schedule_response):
    with patch("requests.post", return_value=mock_schedule_response) as mock_post:
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=30)

        result = station_sim_service.schedule_pass(
            station="ICAN",
            start_time=start_time,
            end_time=end_time,
            state="both_busy",
            mission="SCISAT",
        )

        assert result == {"status": "success"}
        mock_post.assert_called_once()


def test_schedule_pass_error(station_sim_service):
    with patch("requests.post", side_effect=Exception("Connection error")) as mock_post:
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=30)

        with pytest.raises(HTTPException) as exc_info:
            station_sim_service.schedule_pass(
                station="ICAN",
                start_time=start_time,
                end_time=end_time,
                state="both_busy",
                mission="SCISAT",
            )

        assert exc_info.value.status_code == 503
        mock_post.assert_called_once()


def test_query_state_at_success(station_sim_service, mock_state_response):
    with patch("requests.get", return_value=mock_state_response) as mock_get:
        query_time = datetime.now()

        result = station_sim_service.query_state_at(
            station="ICAN", query_time=query_time
        )

        assert result == {"status": "success"}
        mock_get.assert_called_once()


def test_query_state_at_error(station_sim_service):
    with patch("requests.get", side_effect=Exception("Connection error")) as mock_get:
        query_time = datetime.now()

        with pytest.raises(HTTPException) as exc_info:
            station_sim_service.query_state_at(station="ICAN", query_time=query_time)

        assert exc_info.value.status_code == 503
        mock_get.assert_called_once()


def test_query_busy_times_success(station_sim_service, mock_busy_times_response):
    with patch("requests.get", return_value=mock_busy_times_response) as mock_get:
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=24)

        result = station_sim_service.query_busy_times(
            station="ICAN", start_time=start_time, end_time=end_time
        )

        assert result == [
            {
                "start_time": "2024-01-01T00:00:00",
                "end_time": "2024-01-01T01:00:00",
                "state": "both_busy",
                "mission": "SCISAT"
            }
        ]
        mock_get.assert_called_once()


def test_query_busy_times_error(station_sim_service):
    with patch("requests.get", side_effect=Exception("Connection error")) as mock_get:
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=24)

        with pytest.raises(HTTPException) as exc_info:
            station_sim_service.query_busy_times(
                station="ICAN", start_time=start_time, end_time=end_time
            )

        assert exc_info.value.status_code == 503
        mock_get.assert_called_once()
