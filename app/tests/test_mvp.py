from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timedelta

client = TestClient(app)


def test_get_request():
    response = client.get("/api/v1/request/")
    now = datetime.now()
    expected = [
        {
            "requestType": "Contact",
            "mission": "SCI",
            "satellite": "SCISAT 1",
            "station": "Inuvik Northwest",
            "orbit": "",
            "uplink": 1,
            "telemetry": 1,
            "science": 0,
            "startTime": "2024-11-24T20:14:03.550765",
            "endTime": "2024-11-24T20:34:03.550775",
            "duration": 1200.00001,
            "aos": now.isoformat(),
            "rf_on": (now + timedelta(minutes=2)).isoformat(),
            "rf_off": (now + timedelta(minutes=18)).isoformat(),
            "los": (now + timedelta(minutes=20)).isoformat(),
        }
    ]
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == expected


if __name__ == "__main__":
    test_get_request()
