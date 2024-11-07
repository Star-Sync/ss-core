import unittest
from datetime import datetime
from flask import Flask, json
from flaskr.gs_mock import gs_mock


class TestGSMock(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.add_url_rule("/gs_mock", "gs_mock", gs_mock, methods=["POST"])
        self.client = self.app.test_client()

    def test_gs_mock_success(self):
        payload = {
            "start": "2023-01-01 00:00:00",
            "end": "2023-01-01 01:00:00",
            "delta": 60,
        }
        response = self.client.post("/gs_mock", json=payload)
        data = json.loads(response.data)
        expected_response = [True]
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertTrue(all(isinstance(item, bool) for item in data))

    def test_gs_mock_method_not_allowed(self):
        response = self.client.get("/gs_mock")
        self.assertEqual(response.status_code, 405)

    def test_gs_mock_missing_json(self):
        response = self.client.post("/gs_mock", json={})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Missing JSON in request")

    def test_gs_mock_invalid_date_format(self):
        payload = {
            "start": "2023-01-01",
            "end": "2023-01-01 01:00:00",
            "delta": 15,
        }
        response = self.client.post("/gs_mock", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_gs_mock_missing_parameters(self):
        payload = {"start": "2023-01-01 00:00:00", "end": "2023-01-01 01:00:00"}
        response = self.client.post("/gs_mock", json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Missing JSON in request")

    def test_response_is_reproducable(self):
        payload = {
            "start": "2023-01-01 00:00:00",
            "end": "2023-01-01 01:00:00",
            "delta": 15,
            "seed": 42,
        }
        response1 = self.client.post("/gs_mock", json=payload)
        response2 = self.client.post("/gs_mock", json=payload)
        self.assertEqual(response1.data, response2.data)

    def test_response_is_not_reproducable(self):
        payload = {
            "start": "2023-01-01 00:00:00",
            "end": "2023-01-03 01:00:00",
            "delta": 15,
        }
        response1 = self.client.post("/gs_mock", json=payload)
        response2 = self.client.post("/gs_mock", json=payload)
        if response1.data == response2.data:
            response2 = self.client.post("/gs_mock", json=payload)
        self.assertNotEqual(response1.data, response2.data)


if __name__ == "__main__":
    unittest.main()
