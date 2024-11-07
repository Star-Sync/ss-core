from datetime import datetime
from flask import request, jsonify
import numpy as np
from pydantic import BaseModel
from typing import List


class MockRequest(BaseModel):
    start: datetime
    end: datetime
    delta_minutes: int


def gs_mock():
    print("gs_mock")
    if request.method != "POST":
        return jsonify({"error": "Method not allowed"}), 405
    if not request.json or not all(
        key in request.json for key in ["start", "end", "delta"]
    ):
        return jsonify({"error": "Missing JSON in request"}), 400

    start = request.json.get("start")
    end = request.json.get("end")
    delta = request.json.get("delta")

    start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    delta = int(delta)

    mr = MockRequest(start=start, end=end, delta_minutes=delta)

    random_array = generate_mock_data(mr)
    # so, jsonify wil return a json object right
    # and itll will jsonify the python boolean values
    # meaning itll return JS boolean values
    # (true and false, not "True" and "False", nor 1 and 0)
    return jsonify(random_array)


def generate_mock_data(request: MockRequest) -> List[bool]:
    start = request.start
    end = request.end
    delta = request.delta_minutes

    start = start.timestamp()
    end = end.timestamp()

    if start is None or end is None or delta is None:
        raise ValueError("Missing parameters")

    # find the number of delta intervals between start and end
    size = int((end - start) / delta)
    random_array = np.random.choice([True, False], size=size).tolist()
    return random_array
