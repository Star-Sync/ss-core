import uuid
from pydantic import BaseModel, Field


class ExclusionConeCreateModel(BaseModel):
    """
    This is a Pydantic model class that represents the exclusion cone;
    Only used for creation of new resources.
    """

    mission: str = Field(
        description="Name of the mission",
        examples=["SCISAT"],
    )
    angle_limit: float = Field(
        description="The limiting angle between the two objects.", examples=[5.0]
    )
    interfering_satellite: str = Field(
        description="The satellite which must be deconflicted against.",
        examples=["OTHER SAT"],
    )
    satellite_id: uuid.UUID = Field(
        description="The satellite ID the request is for",
        examples=["7b16adda-0dfc-48d0-9902-0da6da504a71"],
    )
    gs_id: int = Field(
        description="The station for which the exclusion cone will apply.", examples=[1]
    )


class ExclusionConeModel(ExclusionConeCreateModel):
    """
    This is a Pydantic model class that represents the exclusion cone.
    """

    id: uuid.UUID = Field(
        description="ID of the exclusion cone",
        examples=["4ff2dab7-bffe-414d-88a5-1826b9fea8df"],
    )
