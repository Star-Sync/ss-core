from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RFTimeRequestModel(BaseModel):
    mission: str = Field(
        description="Name of the mission making the request",
        example="SCISAT"
    )
    satellite: str = Field(
        description="Name of the satellite the request is for",
        example="SCISAT 1"
    )
    startTime: datetime = Field(
        description="The beginning of the time window during which the requested time should be provided in",
        example="2024-10-15T00:00:00"
    )
    endTime: datetime = Field(
        description="The end of the time window during which the requested time should be provided in",
        example="2024-10-15T23:59:59"
    )
    uplink: float = Field(
        description="Time in seconds that the mission is requesting uplink support",
        example=6000
    )
    downlink: float = Field(
        description="Time in seconds that the mission is requesting support for downlinking spacecraft telemetry",
        example=6000
    )
    science: float = Field(
        description="Time in seconds that the mission is requesting support for downlinking science data",
        example=1500
    )
    passNum: Optional[int] = Field(
        default=1,
        description="The minimum number of passes that should be provided to the mission in support of this request",
        example=2
    )


class ContactRequestModel(BaseModel):
    mission: str = Field(
        description="Name of the mission making the request",
        example="SCISAT"
    )
    satellite: str = Field(
        description="Name of the satellite the request is for",
        example="SCISAT-1"
    )
    station: str = Field(
        description="The station the request is for",
        example="Inuvik"
    )
    orbit: str = Field(
        description="The orbit number of the satellite at the time of AOS",
        example="SCISAT-1234"
    )
    uplink: bool = Field(
        description="Is an uplink required for this contact",
        example=True
    )
    telemetry: bool = Field(
        description="Is telemetry downlink required for this contact",
        example=True
    )
    science: bool = Field(
        description="Is science downlink required for this contact",
        example=False
    )
    aos: datetime = Field(
        description="Time of the Acquisition of Signal for the contact",
        example="2024-10-15T12:00:00"
    )
    rf_on: datetime = Field(
        description="Time at which the elevation angle satisfies station mask for a given ground station",
        example="2024-10-15T12:05:00"
    )
    rf_off: datetime = Field(
        description="Time at which the elevation angle satisfies station mask for a given ground station",
        example="2024-10-15T12:45:00"
    )
    los: datetime = Field(
        description="Time of the Loss of Signal for the contact",
        example="2024-10-15T13:00:00"
    )
