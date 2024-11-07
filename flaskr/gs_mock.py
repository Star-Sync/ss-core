import datetime
from flask import jsonify
import numpy as np

from dataclasses import dataclass


@dataclass
class mockRequest:
    start: datetime
    end: datetime
    delta: int


def generate_mock_data(request: mockRequest):
    start = request.start
    end = request.end
    delta = request.delta

    # find the number of delta intervals between start and end
    if start is None or end is None or delta is None:
        return jsonify({"error": "Missing parameters"}), 400

    size = int((end - start) / delta)
    random_array = np.random.choice([True, False], size=size).tolist()

    return jsonify(random_array)
