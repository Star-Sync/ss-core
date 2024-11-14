from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


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
