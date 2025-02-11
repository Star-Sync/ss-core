# from __future__ import annotations
import uuid
from skyfield.sgp4lib import EarthSatellite
from sqlmodel import Relationship, SQLModel, Field
from typing import List, Optional
from typing import TYPE_CHECKING
from app.entities.ExclusionCone import ExclusionCone


class Satellite(SQLModel, table=True):  # type: ignore
    __tablename__: str = "satellites"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    tle: str
    uplink: float
    telemetry: float
    science: float
    priority: int

    ex_cones: list["ExclusionCone"] = Relationship(
        back_populates="satellite", sa_relationship_kwargs={"lazy": "immediate"}
    )  # , sa_relationship_kwargs={"lazy": "immediate"}

    # def __init__(
    #     self,
    #     id: Optional[int] = None,
    #     name: str = "",
    #     tle: str = "",
    #     uplink: float = 0,
    #     downlink: float = 0,
    #     science: float = 0,
    #     priority: int = 0,
    #     # ex_cone: Optional[List[ExclusionCone]] = None,
    # ):
    #     self.id = id
    #     self.name = name
    #     self.tle = tle
    #     self.uplink = uplink
    #     self.telemetry = downlink
    #     self.science = science
    #     # self.ex_cone = ex_cone
    #     self.priority = priority

    def get_sf_sat(self) -> EarthSatellite:
        tle_lines = self.tle.splitlines()
        satellite = EarthSatellite(tle_lines[1], tle_lines[2], tle_lines[0])
        return satellite

    def __repr__(self):
        return f"Satellite(name={self.name})"
