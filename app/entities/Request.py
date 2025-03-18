from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from ..entities.GroundStation import GroundStation
from pydantic import ConfigDict

if TYPE_CHECKING:
    from app.entities.Satellite import Satellite


class RFRequest(SQLModel, table=True):
    """RF Request entity for database storage"""

    __tablename__ = "rf_request"  # type: ignore
    model_config = ConfigDict(arbitrary_types_allowed=True)  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    mission: str
    satellite_id: UUID = Field(foreign_key="satellites.id")
    start_time: datetime
    end_time: datetime
    contact_id: Optional[UUID]
    scheduled: bool = Field(default=False)
    priority: int  # Higher is better
    uplink_time_requested: int
    downlink_time_requested: int
    science_time_requested: int
    min_passes: int
    ground_station_id: Optional[int] = Field(
        default=None, foreign_key="ground_stations.id"
    )
    time_remaining: int
    num_passes_remaining: int

    # copying over from old RFTime class
    def get_priority_weight(self) -> float:
        tot_time = (
            self.uplink_time_requested
            + self.downlink_time_requested
            + self.science_time_requested
        )
        time_period = self.end_time - self.start_time

        return (self.end_time - datetime.now()).total_seconds() * (
            tot_time / time_period.total_seconds()
        )

    def set_time_remaining(self, time_booked: int):
        self.timeRemaining = self.time_remaining - time_booked

    def decrease_pass(self):
        self.num_passes_remaining -= 1

    def __repr__(self):
        return (
            f"RFTime(gs={self.ground_station_id}, sat={self.satellite_id}, "
            f"start={self.start_time}, end={self.end_time}, dur={(self.end_time-self.start_time).total_seconds()}s)"
        )

    # satellite: Optional["Satellite"] = Relationship(back_populates="requests")
    # contact: Optional["Contact"] = Relationship()
    # ground_station: Optional["GroundStation"] = Relationship()


class ContactRequest(SQLModel, table=True):
    """Contact Request entity for database storage"""

    __tablename__ = "contact_request"  # type: ignore
    model_config = ConfigDict(arbitrary_types_allowed=True)  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    mission: str
    satellite_id: UUID = Field(foreign_key="satellites.id")
    start_time: datetime
    end_time: datetime
    contact_id: Optional[UUID]
    scheduled: bool = Field(default=False)
    priority: int  # Higher is better
    ground_station_id: Optional[int] = Field(
        default=None, foreign_key="ground_stations.id"
    )
    orbit: int
    uplink: bool
    telemetry: bool
    science: bool
    aos: datetime | None
    los: datetime | None
    rf_on: datetime | None
    rf_off: datetime | None
    duration: int

    # satellite: Optional["Satellite"] = Relationship(back_populates="requests")
    # contact: Optional["Contact"] = Relationship()
    # ground_station: Optional["GroundStation"] = Relationship()

    def __repr__(self):
        duration_str = "N/A"
        if self.aos and self.los:
            duration_str = f"{(self.los-self.aos).total_seconds()}s"
        return (
            f"Contact(gs={self.ground_station_id}, sat={self.satellite_id}, "
            f"start={self.aos}, end={self.los}, dur={duration_str})"
        )


# RequestBase = Union[RFRequest, ContactRequest]
