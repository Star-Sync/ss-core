from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timedelta

client = TestClient(app)


def test_get_request():
    pass


if __name__ == "__main__":
    test_get_request()
