import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field


class RFTimeRequestModel(BaseModel):
    missionName: str = Field(
        description="Name of the mission making the request", example="SCISAT"
    )
    # will have to rename the field to satelliteName and supply the actual name of the satellite
    satelliteId: str = Field(
        description="Name of the satellite the request is for", example="1"
    )
    # the example times would probably have to be modified eventually
    # this is just to prevent confusion when trying out api endpoints through swagger
    startTime: datetime = Field(
        description="The beginning of the time window during which the requested time should be provided in",
        example=datetime.now() + timedelta(minutes=30),
    )
    endTime: datetime = Field(
        description="The end of the time window during which the requested time should be provided in",
        example=datetime.now() + timedelta(days=1, minutes=30),
    )
    uplinkTime: float = Field(
        description="Time in seconds that the mission is requesting uplink support",
        example=600,
    )
    downlinkTime: float = Field(
        description="Time in seconds that the mission is requesting support for downlinking spacecraft telemetry",
        example=600,
    )
    scienceTime: float = Field(
        description="Time in seconds that the mission is requesting support for downlinking science data",
        example=150,
    )
    minimumNumberOfPasses: Optional[int] = Field(
        default=1,
        description="The minimum number of passes that should be provided to the mission in support of this request",
        example=2,
    )


class ContactRequestModel(BaseModel):
    missionName: str = Field(
        description="Name of the mission making the request", example="SCISAT"
    )
    # will have to rename the field to satelliteName and supply the actual name of the satellite
    satelliteId: str = Field(
        description="Name of the satellite the request is for", example="1"
    )
    location: str = Field(
        description="The station the request is for", example="Inuvik Northwest"
    )
    orbit: str = Field(
        description="The orbit number of the satellite at the time of AOS",
        example="SCISAT-1234",
    )
    uplink: bool = Field(
        description="Is an uplink required for this contact", example=True
    )
    telemetry: bool = Field(
        description="Is telemetry downlink required for this contact", example=True
    )
    science: bool = Field(
        description="Is science downlink required for this contact", example=False
    )
    # the example times would probably have to be modified eventually
    aosTime: datetime = Field(
        description="Time of the Acquisition of Signal for the contact",
        example=datetime.now() + timedelta(minutes=30),
    )
    rfOnTime: datetime = Field(
        description="Time at which the elevation angle satisfies station mask for a given ground station",
        example=datetime.now() + timedelta(minutes=32),
    )
    rfOffTime: datetime = Field(
        description="Time at which the elevation angle satisfies station mask for a given ground station",
        example=datetime.now() + timedelta(minutes=48),
    )
    losTime: datetime = Field(
        description="Time of the Loss of Signal for the contact",
        example=datetime.now() + timedelta(minutes=50),
    )


class GeneralContactResponseModel(BaseModel):
    """
    This is a general response model for both RF time and contact requests.
    """

    requestType: str = Field(
        description="Type of the request (either RF or Contact)", example="RFTime"
    )
    mission: str = Field(
        description="Name of the mission making the request", example="SCISAT"
    )
    satellite: str = Field(
        description="Name of the satellite the request is for", example="SCISAT-1"
    )
    station: str = Field(description="The station the request is for", example="Inuvik")
    orbit: Optional[str] = Field(
        description="The orbit number of the satellite at the time of AOS",
        example="SCISAT-1234",
    )
    uplink: int = Field(
        description="Is an uplink required for this contact", example=True
    )
    telemetry: int = Field(
        description="Is telemetry downlink required for this contact", example=True
    )
    science: int = Field(
        description="Is science downlink required for this contact", example=False
    )
    startTime: datetime = Field(
        description="The beginning of the time window during which the requested time will be provided in",
        example="2024-10-15T12:00:00",
    )
    endTime: datetime = Field(
        description="The end of the time window during which the requested time will be provided in",
        example="2024-10-15T12:20:00",
    )
    duration: float = Field(
        description="Duration of the request in seconds", example=1200
    )
    aos: Optional[datetime] = Field(
        description="Time of the Acquisition of Signal for the contact",
        example="2024-10-15T12:00:00",
    )
    rf_on: Optional[datetime] = Field(
        description="Time at which the elevation angle satisfies station mask for a given ground station",
        example="2024-10-15T12:05:00",
    )
    rf_off: Optional[datetime] = Field(
        description="Time at which the elevation angle satisfies station mask for a given ground station",
        example="2024-10-15T12:15:00",
    )
    los: Optional[datetime] = Field(
        description="Time of the Loss of Signal for the contact",
        example="2024-10-15T12:20:00",
    )

    class Config:
        # Pydantic's default datetime format to serialize `datetime` to ISO 8601 string
        json_encoders = {datetime: lambda v: v.isoformat() if v is not None else None}
