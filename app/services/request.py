#  type: ignore
# ^ remove the type: ignore from the class definition when
#  we have the correct basic types
from copy import deepcopy
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List
from app.entities import GeneralContact
from skyfield.api import load
from app.entities.Visibility import Visibility
from app.entities.GroundStation import GroundStation
from ..entities.RFTime import RFTime
from ..entities.Contact import Contact
from ..entities.Satellite import Satellite
from ..entities.GeneralContact import GeneralContact
from ..models.request import (
    GeneralContactResponseModel,
    RFTimeRequestModel,
    ContactRequestModel,
)
from skyfield.api import utc
from app.services.db import get_db
from fastapi import Depends
from sqlmodel import Session

############################### Set up of static values and objects ###############################
db: Session = Depends(get_db)

time_format = "%Y-%m-%dT%H:%M:%S"

tle1 = """SCISAT 1
1 27858U 03036A   24298.42572809  .00002329  00000+0  31378-3 0  9994
2 27858  73.9300 283.7690 0006053 131.3701 228.7996 14.79804256142522"""
tle2 = """NEOSSAT
1 39089U 13009D   24298.50343230  .00000620  00000+0  23091-3 0  9992
2 39089  98.4036 122.5021 0010164 233.8050 126.2197 14.35350046610553"""

s1 = Satellite(
    name="SCISAT 1", tle=tle1, uplink=150, telemetry=150, science=150, priority=4
)
s2 = Satellite(
    name="NEOSSAT", tle=tle2, uplink=150, telemetry=150, science=150, priority=4
)

g1 = GroundStation(
    name="Inuvik Northwest",
    lat=68.3195,
    lon=-133.549,
    height=102.5,
    mask=5,
    uplink=150,
    downlink=150,
    science=150,
)
g2 = GroundStation(
    name="Prince Albert",
    lat=53.2124,
    lon=-105.934,
    height=490.3,
    mask=5,
    uplink=150,
    downlink=150,
    science=150,
)
g3 = GroundStation(
    name="Gatineau Quebec",
    lat=45.5846,
    lon=-75.8083,
    height=240.1,
    mask=5,
    uplink=150,
    downlink=150,
    science=150,
)

# db.add([g1, g2, g3])
# db.commit()
# db.add_all([s1, s2])
# db.commit()

static_satellites: dict[str, Satellite] = {"1": s1, "2": s2}
static_ground_stations: List[GroundStation] = [g1, g2, g3]

# Insert 1 request into the _db_contact_times
r1 = Contact(
    mission="SCI",
    satellite=static_satellites.get("1"),
    station=static_ground_stations[0],
    uplink=True,
    telemetry=True,
    science=False,
    aos=datetime.now(),
    rf_on=datetime.now() + timedelta(minutes=2),
    rf_off=datetime.now() + timedelta(minutes=18),
    los=datetime.now() + timedelta(minutes=20),
)

_db_contact_times: List[GeneralContact] = [r1]
_db_requests: List[GeneralContact] = [r1]

###################################################################################################


def get_db_contact_times() -> List[GeneralContact]:
    return _db_contact_times


def schedule(request):
    # get existing bookings and requests (currently in-memory list)
    global _db_requests
    global _db_contact_times

    # Use deepcopy to prevent mutating global list directly
    current: List[GeneralContact] = deepcopy(_db_requests)

    # Add the new request
    current.append(request)

    # Sort the requests by earliest end time
    current.sort(key=lambda v: v.end_time if isinstance(v, RFTime) else v.los)

    # Update the global list
    _db_requests = deepcopy(current)

    _db_contact_times = algo(current)


def schedule_rf(request: RFTimeRequestModel):
    # Map the request to an RFTime object
    rf_time: RFTime = _map_rftime_model_to_object(request)
    schedule(rf_time)


def schedule_contact(request: ContactRequestModel):
    # Map the request to an RFTime object
    contact: Contact = _map_contact_model_to_object(request)
    schedule(contact)


def algo(reqs: List[GeneralContact]) -> List[GeneralContact]:
    bookings: List[GeneralContact] = []

    requests: List[GeneralContact] = deepcopy(reqs)

    # iterate through the list, pick out Contact Requests and force into bookings
    for req in requests:
        if isinstance(req, Contact):
            booking = Contact(
                mission=req.mission,
                satellite=req.satellite,
                station=req.satellite,
                uplink=req.uplink,
                telemetry=req.telemetry,
                science=req.science,
                aos=req.aos,
                rf_on=req.rf_on,
                rf_off=req.rf_off,
                los=req.los,
                orbit=req.orbit,
            )
            bookings.append(booking)
            requests.remove(req)

    slots = get_slots(requests)

    # not the most optimal; complexity O(S*R) where S is Slots, and R is Requests
    # does not consider any edge cases (ex. no more room for scheduling - it would schedule in the sequential order)
    for slot in slots:
        if len(requests) == 0:
            break
        for req in requests:

            # determine the end time of last scheduled request (ensure no conflicts)
            if len(bookings) != 0:
                last = bookings[len(bookings) - 1]
                last_end_time = last.end_time if isinstance(last, RFTime) else last.los
                if slot.start < last_end_time:
                    break  # overlap with scheduled request

            if isinstance(req, RFTime):
                req: RFTime = req
                if (req.start_time <= slot.start <= req.end_time) and (
                    req.start_time <= slot.end <= req.end_time
                ):  # The time frame of slot must fit in the request
                    if (
                        slot.sat.name == req.satellite.name and req.timeRemaining >= 0
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
                        req.set_time_remaining(slot.dur)
                        req.decrease_pass()

                        if req.timeRemaining <= 0:
                            requests.remove(req)  # remove from the list of requests
                        break
    return bookings


def get_slots(requests: List[GeneralContact]):
    # integrate with gs_mock to filter out unavailable times
    return get_visibilities(requests=requests)


def get_visibilities(requests: List[GeneralContact]) -> List[Visibility]:
    """
    Get the availability windows for the all the requests in the list
    Return list of Visibility objects
    """
    ts = load.timescale()

    # in a final implementation ground station (gss) list needs to be retrieved from the DB
    global static_ground_stations

    satellites: Dict[str, Satellite] = {}

    # determine the lower and higher time bound for visibility search
    lowest = datetime.strptime("9999-01-01T00:00:00", time_format)
    highest = datetime.strptime("1900-01-01T00:00:00", time_format)

    visibilities: List[Visibility] = []

    # for the request of type Contact, for now we assume that aos and los parameters will comply with GSs station mask
    for req in requests:
        if isinstance(req, RFTime):
            r: RFTime = req
            lowest = min(r.start_time, lowest)
            highest = max(r.end_time, highest)
        else:
            r: Contact = req
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

            for ti, event in zip(t, events):
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


def _map_rftime_model_to_object(req: RFTimeRequestModel) -> RFTime:
    global static_satellites
    sat = static_satellites.get(req.satelliteId)

    if sat is None:
        raise ValueError(
            f"Satellite {req.satelliteId} does not exist in the static map."
        )

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


def _map_contact_model_to_object(req: ContactRequestModel) -> Contact:
    global static_satellites
    global static_ground_stations

    sat = static_satellites.get(req.satelliteId)
    if sat is None:
        raise ValueError(
            f"Satellite {req.satelliteId} does not exist in the static map."
        )

    gs = None
    for station in static_ground_stations:
        if station.name == req.location:
            gs = station
            break
    if gs is None:
        raise ValueError(
            f"Ground Station {req.location} does not exist in the static map."
        )

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
            station=request.station.name,
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
