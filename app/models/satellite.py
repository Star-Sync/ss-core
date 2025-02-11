from typing import List, Optional
import uuid
from pydantic import BaseModel, Field
from app.models.exclusion_cone import ExclusionConeModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .exclusion_cone import ExclusionConeModel


class SatelliteCreateModel(BaseModel):
    """
    A pydantic model class representing the satellite. Only used for creation of new resources.
    """

    name: str = Field(
        description="Name of the satellite",
        examples=["SCISAT 1"],
    )
    tle: str = Field(
        description="TLE of the satellite",
        examples=[
            "SCISAT 1\n1 27858U 03036A   24298.42572809  .00002329  00000+0  31378-3 0  9994\n2 27858  73.9300 283.7690 0006053 131.3701 228.7996 14.79804256142522"
        ],
    )
    uplink: float = Field(description="Uplink data rate in Kbps", examples=[40.0])
    telemetry: float = Field(description="Downlink data rate in Mbps", examples=[100.0])
    science: float = Field(description="Science data rate in Mbps", examples=[100.0])
    priority: int = Field(description="Priority of the satellite", examples=[1])


class SatelliteModel(SatelliteCreateModel):
    """
    A pydantic model class representing the satellite.
    """

    id: uuid.UUID = Field(
        description="ID of the satellite",
        examples=["7b16adda-0dfc-48d0-9902-0da6da504a71"],
    )
    ex_cones: Optional[List["ExclusionConeModel"]] = Field(
        default_factory=list,
        description="List of exclusion cones",
        examples=[[]],
    )
