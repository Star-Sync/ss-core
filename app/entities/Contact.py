from datetime import datetime
from typing import TYPE_CHECKING, Optional
from app.entities.GroundStation import GroundStation

if TYPE_CHECKING:
    from app.entities.Satellite import Satellite


class Contact:

    def __init__(
        self,
        id,
        mission: str,
        satellite: "Satellite",
        station: GroundStation,
        uplink: bool,
        telemetry: bool,
        science: bool,
        aos: datetime,
        rf_on: datetime,
        rf_off: datetime,
        los: datetime,
        orbit: Optional[str] = "",
    ):
        self.id = id
        self.mission = mission
        self.satellite = satellite
        self.station = station
        self.uplink = uplink
        self.telemetry = telemetry
        self.science = science
        self.aos = aos
        self.rf_on = rf_on
        self.rf_off = rf_off
        self.los = los
        self.orbit = orbit

    def __repr__(self):
        return (
            f"Contact(gs={self.station.name}, sat={self.satellite.name}, "
            f"start={self.aos}, end={self.los}, dur={(self.los-self.aos).total_seconds()}s)"
        )


class RFTime:
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
        station: Optional[GroundStation] = None,
    ):
        self.mission = mission
        self.satellite = satellite
        self.start_time = start_time
        self.end_time = end_time
        self.uplink = uplink
        self.telemetry = telemetry
        self.science = science
        self.pass_num = pass_num
        self.station = station
        self.timeRemaining = max(self.uplink, self.telemetry, self.science)
        self.passNumRemaining = pass_num
        self.science = science
        self.pass_num = pass_num
        self.timeRemaining = max(self.uplink, self.telemetry, self.science)
        self.passNumRemaining = pass_num

    def get_priority_weight(self) -> float:
        tot_time = self.uplink + self.telemetry + self.science
        time_period = self.end_time - self.start_time

        return (self.end_time - datetime.now()).total_seconds() * (
            tot_time / time_period.total_seconds()
        )

    def set_time_remaining(self, time_booked: int):
        self.timeRemaining = self.timeRemaining - time_booked

    def decrease_pass(self):
        self.passNumRemaining -= 1

    def __repr__(self):
        return (
            f"RFTime(gs={self.station.name}, sat={self.satellite.name}, "
            f"start={self.start_time}, end={self.end_time}, dur={(self.end_time-self.start_time).total_seconds()}s)"
        )
