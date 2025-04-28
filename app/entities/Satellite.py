import uuid
from skyfield.sgp4lib import EarthSatellite  # type: ignore
from sqlmodel import Relationship, SQLModel, Field  # type: ignore
from sqlalchemy.orm import Mapped
from typing import List
from app.entities.ExclusionCone import ExclusionCone


class Satellite(SQLModel, table=True):
    __tablename__: str = "satellites"  # type: ignore

    id: uuid.UUID = Field(primary_key=True)
    name: str
    tle: str
    uplink: float
    telemetry: float
    science: float
    priority: int
    ex_cones: Mapped[List["ExclusionCone"]] = Relationship(back_populates="satellite")

    # this init will most likely be removed soon
    def __init__(
        self,
        id: uuid.UUID | None = None,
        name: str = "",
        tle: str = "",
        uplink: float = 0,
        telemetry: float = 0,
        science: float = 0,
        priority: int = 0,
        # ex_cone: Optional[List[ExclusionCone]] = None,
    ):
        self.id = id if id is not None else uuid.uuid4()
        self.name = name
        self.tle = tle
        self.uplink = uplink
        self.telemetry = telemetry
        self.science = science
        # self.ex_cone = ex_cone
        self.priority = priority

    def get_sf_sat(self) -> EarthSatellite:
        try:
            tle_lines = self.tle.splitlines()
            if len(tle_lines) < 3:
                raise ValueError(
                    f"Invalid TLE format for satellite {self.name}. Expected 3 lines, got {len(tle_lines)}"
                )

            # Ensure we have the name, line 1, and line 2
            name = tle_lines[0].strip()
            line1 = tle_lines[1].strip()
            line2 = tle_lines[2].strip()

            # Validate TLE format
            if not line1.startswith("1 ") or not line2.startswith("2 "):
                raise ValueError(
                    f"Invalid TLE format for satellite {self.name}. Lines must start with '1 ' and '2 '"
                )

            satellite = EarthSatellite(line1, line2, name)
            return satellite
        except Exception as e:
            raise ValueError(
                f"Error creating skyfield satellite for {self.name}: {str(e)}"
            )

    def __repr__(self):
        return f"Satellite(name={self.name})"
