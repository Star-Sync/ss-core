import asyncio
from datetime import datetime
from typing import List, Optional

from app.entities.GroundStation import GroundStation
from app.entities.Satellite import Satellite
from app.models.request import GeneralContactResponseModel

# Global list of RF Time Requests, stored in memory
# Temporary solution until we have a database
existing_bookings: List["GeneralContact"] = []
# Lock for thread safety
lock = asyncio.Lock()

class GeneralContact:
    def __init__(
        self,
        mission: str,
        satellite: Satellite,
        station: GroundStation,
        uplink: bool,
        telemetry: bool,
        science: bool,
        start_time: datetime,
        end_time: datetime,
        orbit: Optional[str] = "",
        aos: Optional[datetime] = None,
        rf_on: Optional[datetime] = None,
        rf_off: Optional[datetime] = None,
        los: Optional[datetime] = None,
        pass_num: Optional[int] = 1
    ):
        self.mission = mission
        self.satellite = satellite
        self.station = station
        self.orbit = orbit
        self.uplink = uplink
        self.telemetry = telemetry
        self.science = science
        self.start_time = start_time
        self.end_time = end_time
        self.aos = aos
        self.rf_on = rf_on
        self.rf_off = rf_off
        self.los = los
        self.timeRemaining = max(self.uplink, self.telemetry, self.science)
        self.passNumRemaining = pass_num

    def get_priority_weight(self) -> int:
        tot_time = self.uplink + self.downlink + self.science
        time_period = self.end_time - self.start_time
        
        return (self.end_time - datetime.now()).total_seconds()*(tot_time/time_period.total_seconds())
    
    def set_time_remaining(self, time_booked: int) -> int:
        self.timeRemaining = self.timeRemaining - time_booked
    
    def decrease_pass(self):
        self.passNumRemaining -= 1

    def __repr__(self):
        return (f"GeneralContact(gs={self.station.name}, sat={self.satellite.name}, "
                f"start={self.start_time}, end={self.end_time}, dur={(self.end_time-self.start_time).total_seconds()}s)")
    
    def convert_to_model(self) -> GeneralContactResponseModel:
        return GeneralContactResponseModel(
            mission=self.mission,
            satellite=self.satellite.name,
            station=self.station.name,
            uplink=self.uplink,
            telemetry=self.telemetry,
            science=self.science,
            startTime=self.start_time,
            endTime=self.end_time,
            duration=(self.end_time - self.start_time).total_seconds(),
            orbit=self.orbit,
            aos=self.aos,
            rf_on=self.rf_on,
            rf_off=self.rf_off,
            los=self.los
        )