from typing import Dict, List, Union
from datetime import datetime
from sqlmodel import Session, select
from skyfield.api import load, utc, Time
from copy import deepcopy
from ..entities.RFTime import RFTime
from ..entities.Contact import Contact
from ..entities.Satellite import Satellite
from ..entities.GroundStation import GroundStation
from ..entities.Visibility import Visibility
from ..models.request import (
    GeneralContactResponseModel,
    RFTimeRequestModel,
    ContactRequestModel,
)
from ..services.db import get_db
from sqlalchemy.orm import joinedload

GeneralContact = Union[RFTime, Contact]


class SchedulerService:
    def __init__(self, db: Session):
        self.db = db
        self.time_format = "%Y-%m-%dT%H:%M:%S"

    def get_db_contact_times(self) -> List[GeneralContact]:
        rf_times: List[RFTime] = list(self.db.exec(select(RFTime)).all())
        contacts: List[Contact] = list(self.db.exec(select(Contact)).all())

        return rf_times + contacts

    def schedule_rf(self, request: RFTimeRequestModel) -> RFTime:
        rf_time = self._map_rftime_model_to_object(request)
        self._schedule(rf_time)
        rf_time = self.db.get(RFTime, rf_time.id)
        if not rf_time:
            raise ValueError("RFTime not found in the DB")

        return rf_time

    def schedule_contact(self, request: ContactRequestModel) -> Contact:
        contact = self._map_contact_model_to_object(request)
        self._schedule(contact)
        contact = self.db.get(Contact, contact.id)
        if not contact:
            raise ValueError("Contact not found in the DB")
        return contact

    def init_db_contact_times(self):
        tle1 = """SCISAT 1\n1 27858U 03036A   24298.42572809  .00002329  00000+0  31378-3 0  9994\n2 27858  73.9300 283.7690 0006053 131.3701 228.7996 14.79804256142522"""
        tle2 = """NEOSSAT\n1 39089U 13009D   24298.50343230  .00000620  00000+0  23091-3 0  9992\n2 39089  98.4036 122.5021 0010164 233.8050 126.2197 14.35350046610553"""

        s1 = Satellite(tle1, 150, 150, 150, "exCone", 4)
        s2 = Satellite(tle2, 150, 150, 150, "exCone", 4)

        g1 = GroundStation(
            "Inuvik Northwest", 68.3195, -133.549, 102.5, 0, 150, 150, 150
        )
        g2 = GroundStation("Prince Albert", 53.2124, -105.934, 490.3, 0, 150, 150, 150)
        g3 = GroundStation(
            "Gatineau Quebec", 45.5846, -75.8083, 240.1, 0, 150, 150, 150
        )

        items = [s1, s2, g1, g2, g3]
        for item in items:
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
        self.db.close()

    def _schedule(self, request: Union[RFTime, Contact]):
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)

        current = self.get_db_contact_times()
        current.sort(key=lambda v: v.end_time if isinstance(v, RFTime) else v.los)

        updated_contact_times = self._algo(current)

        for contact in updated_contact_times:
            self.db.merge(contact)

        self.db.commit()
        self.db.close()

    # Move all your existing helper methods here, converting them to instance methods
    # Remember to remove the db parameter and use self.db instead
    def _algo(self, requests: List[GeneralContact]) -> List[GeneralContact]:
        bookings: List[GeneralContact] = []

        for req in requests:
            if isinstance(req, Contact):
                booking = Contact(
                    mission=req.mission,
                    satellite=req.satellite,
                    station=req.station,
                    uplink=bool(req.uplink),
                    telemetry=bool(req.telemetry),
                    science=bool(req.science),
                    aos=req.aos,
                    rf_on=req.rf_on,
                    rf_off=req.rf_off,
                    los=req.los,
                    orbit=req.orbit,
                )
                bookings.append(booking)
                requests.remove(req)

        slots = self._get_slots(requests)

        # not the most optimal; complexity O(S*R) where S is Slots, and R is Requests
        # does not consider any edge cases (ex. no more room for scheduling - it would schedule in the sequential order)
        for slot in slots:
            if len(requests) == 0:
                break
            for req in requests:
                # determine the end time of last scheduled request (ensure no conflicts)
                if len(bookings) != 0:
                    last = bookings[len(bookings) - 1]
                    last_end_time = (
                        last.end_time if isinstance(last, RFTime) else last.los
                    )
                    if slot.start < last_end_time:
                        break  # overlap with scheduled request

                if isinstance(req, RFTime):
                    if (req.start_time <= slot.start <= req.end_time) and (
                        req.start_time <= slot.end <= req.end_time
                    ):  # The time frame of slot must fit in the request
                        if (
                            slot.sat.name == req.satellite.name
                            and req.timeRemaining >= 0
                        ):  # The time slot must be able to service the satellite
                            booking = RFTime(
                                mission=req.mission,
                                satellite=req.satellite,
                                station=slot.gs,
                                uplink=req.uplink,
                                telemetry=req.telemetry,
                                science=req.science,
                                start_time=slot.start,
                                end_time=slot.end,
                            )
                            bookings.append(booking)

                            # decrease the time remaining
                            # need to change logic such that all passes specified in request are used
                            req.set_time_remaining(int(slot.dur))
                            req.decrease_pass()

                            if req.timeRemaining <= 0:
                                requests.remove(req)  # remove from the list of requests
                            break
        return bookings

    def _get_slots(self, requests: List[GeneralContact]) -> List[Visibility]:
        # integrate with gs_mock to filter out unavailable times
        return self._get_visibilities(requests=requests)

    def _get_visibilities(self, requests: List[GeneralContact]) -> List[Visibility]:
        """
        Get the availability windows for the all the requests in the list
        Return list of Visibility objects
        """
        ts = load.timescale()

        satellites: Dict[str, Satellite] = {}
        static_ground_stations = list(self._get_ground_stations().values())
        # determine the lower and higher time bound for visibility search
        lowest = datetime.strptime("9999-01-01T00:00:00", self.time_format)
        highest = datetime.strptime("1900-01-01T00:00:00", self.time_format)

        visibilities: List[Visibility] = []

        # for the request of type Contact, for now we assume that aos and los parameters will comply with GSs station mask
        for r in requests:
            if isinstance(r, RFTime):
                lowest = min(r.start_time, lowest)
                highest = max(r.end_time, highest)
            else:
                lowest = min(r.aos, lowest)
                highest = max(r.los, highest)

            satellites[r.satellite.name] = r.satellite

        # Three nested for-loops - horrible - I know; will be optimized later
        for s in satellites.values():
            for g in static_ground_stations:
                t, events = s.get_sf_sat().find_events(
                    g.get_sf_geo_position(),
                    ts.from_datetime(lowest.replace(tzinfo=utc)),
                    ts.from_datetime(highest.replace(tzinfo=utc)),
                    g.mask,
                )
                current_rise = None

                for ti, event in zip(t, events):  # type: ignore
                    if event == 0:
                        current_rise = ti.utc_datetime().replace(tzinfo=None)
                    elif event == 2 and current_rise:
                        visibilities.append(
                            Visibility(
                                gs=g,
                                sat=s,
                                start=current_rise,
                                end=ti.utc_datetime().replace(tzinfo=None),
                            )
                        )
                        current_rise = None

        visibilities.sort(key=lambda v: v.start)
        return visibilities

    def _get_satellites(self) -> Dict[str, Satellite]:
        satellites: List[Satellite] = list(self.db.exec(select(Satellite)).all())
        return {str(sat.id): sat for sat in satellites}

    def _get_ground_stations(self) -> Dict[str, GroundStation]:
        ground_stations: List[GroundStation] = list(
            self.db.exec(select(GroundStation)).all()
        )
        return {str(gs.name): gs for gs in ground_stations}

    def _map_rftime_model_to_object(self, req: RFTimeRequestModel) -> RFTime:
        static_satellites: Dict[str, Satellite] = self._get_satellites()
        sat = static_satellites.get(req.satelliteId)
        if not sat:
            raise ValueError(f"Satellite {req.satelliteId} does not exist in the DB")
        return RFTime(
            mission=req.missionName,
            satellite=sat,
            start_time=req.startTime,
            end_time=req.endTime,
            uplink=req.uplinkTime,
            telemetry=req.downlinkTime,
            science=req.scienceTime,
            pass_num=req.minimumNumberOfPasses,
        )

    def _map_contact_model_to_object(self, req: ContactRequestModel) -> Contact:
        static_satellites: Dict[str, Satellite] = self._get_satellites()
        static_ground_stations: Dict[str, GroundStation] = self._get_ground_stations()
        sat = static_satellites.get(req.satelliteId)
        gs = static_ground_stations.get(req.location)
        if not sat:
            raise ValueError(f"Satellite {req.satelliteId} does not exist in the DB")
        if not gs:
            raise ValueError(f"Ground station {req.location} does not exist in the DB")

        return Contact(
            mission=req.missionName,
            satellite=sat,
            station=gs,
            uplink=req.uplink,
            telemetry=req.telemetry,
            science=req.science,
            aos=req.aosTime,
            rf_on=req.rfOnTime,
            rf_off=req.rfOffTime,
            los=req.losTime,
        )


# Service factory for dependency injection
def get_scheduler_service() -> SchedulerService:
    db = next(get_db())
    return SchedulerService(db)


def map_to_response_model(request: GeneralContact) -> GeneralContactResponseModel:
    if isinstance(request, Contact):
        return GeneralContactResponseModel(
            requestType="Contact",
            mission=request.mission,
            satellite=request.satellite.name,
            station=request.station.name,
            orbit=request.orbit,
            uplink=request.uplink,
            telemetry=request.telemetry,
            science=request.science,
            startTime=request.aos,
            endTime=request.los,
            duration=(request.los - request.aos).total_seconds(),
            aos=request.aos,
            rf_on=request.rf_on,
            rf_off=request.rf_off,
            los=request.los,
        )
    elif isinstance(request, RFTime):
        return GeneralContactResponseModel(
            requestType="RFTime",
            mission=request.mission,
            satellite=request.satellite.name,
            station=request.station.name if request.station else "None",
            orbit=None,
            uplink=request.uplink,
            telemetry=request.telemetry,
            science=request.science,
            startTime=request.start_time,
            endTime=request.end_time,
            duration=(request.end_time - request.start_time).total_seconds(),
            aos=None,
            rf_on=None,
            rf_off=None,
            los=None,
        )
    else:
        raise ValueError(f"Unsupported request type: {type(request).__name__}")
