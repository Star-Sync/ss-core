from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from ..entities.GroundStation import GroundStation
from ..entities.Contact import Contact
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
    aos: int
    los: int
    rf_on: int
    rf_off: int
    duration: int

    # satellite: Optional["Satellite"] = Relationship(back_populates="requests")
    # contact: Optional["Contact"] = Relationship()
    # ground_station: Optional["GroundStation"] = Relationship()


# RequestBase = Union[RFRequest, ContactRequest]
