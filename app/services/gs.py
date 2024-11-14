from typing import List
import numpy as np
from ..models.gs import MockRequest


def generate_mock_data(request: MockRequest) -> List[bool]:
    start_epoch = request.start.timestamp()
    end_epoch = request.end.timestamp()
    delta_seconds = request.delta_minutes * 60

    # Set the seed for reproducibility if provided
    if request.seed:
        np.random.seed(request.seed)

    # find the number of delta intervals between start and end
    size = int((end_epoch - start_epoch) / delta_seconds)
    random_array = np.random.choice([True, False], size=size).tolist()
    return random_array
