from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from app.entities.GroundStation import GroundStation
    from app.entities.Satellite import Satellite


class RFTime(SQLModel, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    mission: str
    satellite_id: int = Field(foreign_key="satellite.id")
    satellite: "Satellite" = Relationship(back_populates="rf_times")
    start_time: datetime
    end_time: datetime
    uplink: float
    telemetry: float
    science: float
    pass_num: int = Field(default=1)
    station_id: Optional[int] = Field(default=None, foreign_key="groundstation.id")
    station: Optional["GroundStation"] = Relationship(back_populates="rf_times")
    timeRemaining: float
    passNumRemaining: int

    def __init__(
        self,
        mission: str,
        satellite: "Satellite",
        start_time: datetime,
        end_time: datetime,
        uplink: float,
        telemetry: float,
        science: float,
        pass_num: int = 1,
        station: Optional["GroundStation"] = None,
    ):
        self.mission = mission
        self.satellite = satellite
        self.station = station
        self.start_time = start_time
        self.end_time = end_time
        self.uplink = uplink
        self.telemetry = telemetry
        self.science = science
        self.pass_num = pass_num
        self.timeRemaining = max(self.uplink, self.telemetry, self.science)
        self.passNumRemaining = pass_num

    def get_priority_weight(self) -> int:
        tot_time = self.uplink + self.telemetry + self.science
        time_period = self.end_time - self.start_time

        return int(
            (self.end_time - datetime.now()).total_seconds()
            * (tot_time / time_period.total_seconds())
        )

    def set_time_remaining(self, time_booked: int) -> None:
        self.timeRemaining = self.timeRemaining - time_booked

    def decrease_pass(self):
        self.passNumRemaining -= 1

    def __repr__(self):
        return (
            f"RFTime(gs={self.station_id}, sat={self.satellite_id}, "
            f"start={self.start_time}, end={self.end_time}, dur={(self.end_time-self.start_time).total_seconds()}s)"
        )
