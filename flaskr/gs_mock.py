from datetime import datetime
from flask import request, jsonify
import numpy as np
from pydantic import BaseModel, Field
from typing import List, Optional


class MockRequest(BaseModel):
    start: datetime
    end: datetime
    delta_minutes: int
    seed: Optional[int] = Field(default=None)


def gs_mock():
    if request.method != "POST":
        return jsonify({"error": "Method not allowed"}), 405
    if not request.json or not all(
        key in request.json for key in ["start", "end", "delta"]
    ):
        return jsonify({"error": "Missing JSON in request"}), 400

    start = request.json.get("start")
    end = request.json.get("end")
    delta = request.json.get("delta")
    seed = request.json.get("seed")

    try:
        start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        delta = int(delta)
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {e}"}), 400

    mr = MockRequest(start=start, end=end, delta_minutes=delta, seed=seed)

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
    seed = request.seed

    start = start.timestamp()
    end = end.timestamp()
    delta = delta * 60

    if start is None or end is None or delta is None:
        raise ValueError("Missing parameters")

    # Set the seed for reproducibility if provided
    if seed is not None:
        np.random.seed(seed)

    # find the number of delta intervals between start and end
    size = int((end - start) / delta)
    random_array = np.random.choice([True, False], size=size).tolist()
    return random_array
