from datetime import datetime
from typing import Optional
from app.entities.Satellite import Satellite
from app.entities.GeneralContact import GeneralContact
from app.entities.GroundStation import GroundStation


class RFTime(GeneralContact):
    """
    This is the first type of request. It is more general since user only specifies the satellite and start/end times for which the contact should happen.
    """

    def __init__(
        self,
        mission: str,
        satellite: Satellite,
        start_time: datetime,
        end_time: datetime,
        uplink: float,
        telemetry: float,
        science: float,
        pass_num: int = 1,
        station: Optional[GroundStation] = None,
    ):
        super().__init__(mission, satellite, station)
        self.start_time = start_time
        self.end_time = end_time
        self.uplink = uplink
        self.telemetry = telemetry
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
