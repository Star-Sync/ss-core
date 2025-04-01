import uuid
from sqlmodel import SQLModel, Field, Relationship  # type: ignore
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.entities.Satellite import Satellite


class ExclusionCone(SQLModel, table=True):
    __tablename__: str = "exclusion_cones"  # type: ignore

    id: uuid.UUID = Field(primary_key=True)
    mission: str
    angle_limit: float
    interfering_satellite: uuid.UUID = Field(foreign_key="satellites.id")
    satellite_id: uuid.UUID = Field(foreign_key="satellites.id")
    gs_id: int = Field(foreign_key="ground_stations.id")
    satellite: "Satellite" = Relationship(back_populates="ex_cones")

    # Will most likely be removed soon
    def __init__(
        self,
        mission: str,
        angle_limit: float,
        interfering_satellite: uuid.UUID,
        satellite_id: uuid.UUID,
        gs_id: int,
        id: uuid.UUID | None = None,
    ):
        self.id = id if id is not None else uuid.uuid4()
        self.mission = mission
        self.angle_limit = angle_limit
        self.interfering_satellite = interfering_satellite
        self.satellite_id = satellite_id
        self.gs_id = gs_id
