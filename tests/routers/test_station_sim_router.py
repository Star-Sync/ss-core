import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_schedule_pass_success():
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=30)

    response = client.post(
        "/api/v1/station-sim/ICAN/schedule_pass",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "state": "both_busy",
            "mission": "SCISAT",
        },
    )

    assert response.status_code == 200
    assert "status" in response.json()


def test_schedule_pass_invalid_state():
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=30)

    response = client.post(
        "/api/v1/station-sim/ICAN/schedule_pass",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "state": "invalid_state",
            "mission": "SCISAT",
        },
    )

    assert response.status_code == 422  # Validation error


def test_query_state_at_success():
    query_time = datetime.now()

    response = client.get(
        f"/api/v1/station-sim/ICAN/query_state_at/{query_time.isoformat()}"
    )

    assert response.status_code == 200
    assert "status" in response.json()


def test_query_busy_times_success():
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=24)

    response = client.get(
        "/api/v1/station-sim/ICAN/query_busy_times",
        params={"start_time": start_time.isoformat(), "end_time": end_time.isoformat()},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_query_busy_times_invalid_time_range():
    start_time = datetime.now()
    end_time = start_time - timedelta(hours=1)  # End time before start time

    response = client.get(
        "/api/v1/station-sim/ICAN/query_busy_times",
        params={"start_time": start_time.isoformat(), "end_time": end_time.isoformat()},
    )

    assert response.status_code == 422  # Validation error
