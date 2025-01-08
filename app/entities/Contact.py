from datetime import datetime
from typing import Optional
from app.entities.Satellite import Satellite
from app.entities.GeneralContact import GeneralContact
from app.entities.GroundStation import GroundStation
from app.entities.Satellite import Satellite


class Contact(GeneralContact):
    def __init__(
        self,
        mission: str,
        satellite: Satellite,
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
        super().__init__(mission, satellite, station)
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
