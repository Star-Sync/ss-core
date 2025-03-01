import uuid
from sqlmodel import SQLModel, Field, Relationship  # type: ignore
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.entities.Satellite import Satellite


class ExclusionCone(SQLModel, table=True):
    __tablename__: str = "exclusion_cones"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    mission: str
    angle_limit: float
    interfering_satellite: str
    satellite_id: uuid.UUID = Field(foreign_key="satellites.id")
    gs_id: int = Field(foreign_key="ground_stations.id")
    satellite: "Satellite" = Relationship(back_populates="ex_cones")

    # Will most likely be removed soon
    def __init__(
        self,
        id: uuid.UUID = uuid.uuid4(),
        mission: str = "",
        angle_limit: float = 0,
        interfering_satellite: str = "",
        satellite_id: uuid.UUID = uuid.uuid4(),
        gs_id: int = 1,
    ):
        self.id = id
        self.mission = mission
        self.angle_limit = angle_limit
        self.interfering_satellite = interfering_satellite
        self.satellite_id = satellite_id
        self.gs_id = gs_id
