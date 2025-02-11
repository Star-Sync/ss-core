# from __future__ import annotations
import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.entities.Satellite import Satellite


class ExclusionCone(SQLModel, table=True):  # type: ignore
    __tablename__: str = "exclusion_cones"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    mission: str
    angle_limit: float
    interfering_satellite: str
    satellite_id: uuid.UUID = Field(foreign_key="satellites.id")

    # , sa_relationship_kwargs={"lazy": "immediate"}
    satellite: "Satellite" = Relationship(
        back_populates="ex_cones", sa_relationship_kwargs={"lazy": "immediate"}
    )
    gs_id: int = Field(foreign_key="ground_stations.id")

    def __init__(
        self,
        id: uuid.UUID = uuid.uuid4(),
        mission: str = "",
        angle_limit: float = 0,
        interfering_satellite: str = "",
        satellite_id: uuid.UUID = uuid.uuid4(),
        gs_id: int = 1,
        # satellite_id: int = Field(
        #     foreign_key="satellites.id"  # Foreign key to Satellite
        # ),
        # # satellite: Optional[Satellite] = Relationship(back_populates="exclusion_cones"),
        # gs_id: int = Field(
        #     foreign_key="ground_stations.id"  # Foreign key to GroundStation
        # ),
        # gs: Optional[GroundStation] = Relationship(back_populates="exclusion_cones"),
    ):
        self.id = id
        self.mission = mission
        self.angle_limit = angle_limit
        self.interfering_satellite = interfering_satellite
        self.satellite_id = satellite_id
        self.gs_id = gs_id
