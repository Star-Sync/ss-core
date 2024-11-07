from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import numpy as np
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(
    prefix="/gs",
    tags=["gs"],
    responses={404: {"description": "Not found"}},
)


class MockRequest(BaseModel):
    start: datetime = Field(
        description="Start date and time",
        json_schema_extra={"example": "2021-01-01 00:00:00"},
    )
    end: datetime = Field(
        description="End date and time",
        json_schema_extra={"example": "2021-01-01 01:00:00"},
    )
    delta_minutes: int = Field(
        description="Number of minutes between each data point",
        json_schema_extra={"example": 15},
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducibility",
        json_schema_extra={"example": 41},
    )


@router.post(
    "/mock",
    summary="Generate mock data for ground stations",
    response_model=List[bool],
    response_description="List of boolean values that are equal to the ground stations availability at each time interval",
)
async def gs_mock(request: MockRequest):
    return JSONResponse(content=generate_mock_data(request))


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
