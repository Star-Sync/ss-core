from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from ..entities.Satellite import Satellite
from ..entities.GroundStation import GroundStation
from ..entities.Contact import Contact


class RequestBase(SQLModel, table=False):
    """Base class for all request types"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    mission: str
    satellite_id: UUID = Field(foreign_key="satellite.id")
    start_time: datetime
    end_time: datetime
    contact_id: Optional[UUID] = Field(default=None, foreign_key="contact.id")
    scheduled: bool = Field(default=False)
    priority: int  # Higher is better

    satellite: Optional[Satellite] = Relationship()
    contact: Optional[Contact] = Relationship()


class RFRequest(RequestBase, table=True):
    """RF Request entity for database storage"""

    __tablename__ = "rf_request"  # type: ignore

    uplink_time_requested: int
    downlink_time_requested: int
    science_time_requested: int
    min_passes: int
    ground_station_id: Optional[UUID] = Field(
        default=None, foreign_key="groundstation.id"
    )

    ground_station: Optional[GroundStation] = Relationship()


class ContactRequest(RequestBase, table=True):
    """Contact Request entity for database storage"""

    __tablename__ = "contact_request"  # type: ignore

    ground_station_id: UUID = Field(foreign_key="groundstation.id")
    orbit: int
    uplink: bool
    telemetry: bool
    science: bool
    aos: int
    los: int
    rf_on: int
    rf_off: int
    duration: int
    ground_station: GroundStation = Relationship()
