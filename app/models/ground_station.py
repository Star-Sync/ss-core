from typing import Optional
from pydantic import BaseModel, Field


class GroundStationModel(BaseModel):
    """
    This is a Pydantic model class that represents the ground station.
    """

    id: Optional[int] = Field(
        None, description="ID of the ground station", examples=[1]
    )
    name: str = Field(
        description="Name of the ground station",
        examples=["Inuvik Northwest Territories"],
    )
    lat: float = Field(description="Latitude of the ground station", examples=[68.3195])
    lon: float = Field(
        description="Longitude of the ground station", examples=[-133.549]
    )
    height: float = Field(
        description="Height of the ground station above sea level in meters",
        examples=[102.5],
    )
    mask: int = Field(
        description="Mask angle of the ground station in degrees. (Note: for now the value is the same for Receive and Send)",
        examples=[5],
    )
    uplink: float = Field(description="Uplink data rate in Kbps", examples=[40.0])
    downlink: float = Field(description="Downlink data rate in Mbps", examples=[100.0])
    science: float = Field(description="Science data rate in Mbps", examples=[100.0])
