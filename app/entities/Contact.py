from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.entities.GroundStation import GroundStation
    from app.entities.Satellite import Satellite


class Contact(SQLModel, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    mission: str
    satellite_id: Optional[int] = Field(default=None, foreign_key="satellite.id")
    station_id: Optional[int] = Field(default=None, foreign_key="groundstation.id")
    satellite: "Satellite" = Relationship(back_populates="contacts")
    station: "GroundStation" = Relationship(back_populates="contacts")
    uplink: bool
    telemetry: bool
    science: bool
    aos: datetime
    rf_on: datetime
    rf_off: datetime
    los: datetime
    orbit: Optional[str] = ""

    def __repr__(self):
        return (
            f"Contact(gs={self.station_id}, sat={self.satellite_id}, "
            f"start={self.aos}, end={self.los}, dur={(self.los-self.aos).total_seconds()}s)"
        )
