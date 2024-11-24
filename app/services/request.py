from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Union

from sqlmodel import Session, select

# from app.entities.GeneralContact import GeneralContact
from skyfield.api import load
from app.entities.Visibility import Visibility
from app.entities.GroundStation import GroundStation
from app.services.db import get_db
from ..entities.RFTime import RFTime
from ..entities.Contact import Contact
from ..entities.Satellite import Satellite

from ..models.request import (
    GeneralContactResponseModel,
    RFTimeRequestModel,
    ContactRequestModel,
)
from skyfield.api import utc

GeneralContact = Union[RFTime, Contact]

time_format = "%Y-%m-%dT%H:%M:%S"


def init_db_contact_times(db: Session):
    with db as db:
        tle1 = """SCISAT 1
        1 27858U 03036A   24298.42572809  .00002329  00000+0  31378-3 0  9994
        2 27858  73.9300 283.7690 0006053 131.3701 228.7996 14.79804256142522"""
        tle2 = """NEOSSAT
        1 39089U 13009D   24298.50343230  .00000620  00000+0  23091-3 0  9992
        2 39089  98.4036 122.5021 0010164 233.8050 126.2197 14.35350046610553"""

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
            db.add(item)
            db.commit()
            db.refresh(item)


def get_db_contact_times(db: Session) -> List[GeneralContact]:
    with db as db:
        _db_contact_times: List[GeneralContact] = list(db.exec(select(RFTime)).all())
        _db_contact_times.extend(list(db.exec(select(Contact)).all()))
        return _db_contact_times


def schedule(request: GeneralContact, db: Session):
    db.add(request)
    db.commit()
    db.refresh(request)

    # Retrieve all requests from the database
    current: List[GeneralContact] = get_db_contact_times(db)
    current.sort(key=lambda v: v.end_time if isinstance(v, RFTime) else v.los)

    # Update the contact times using the algorithm
    updated_contact_times = algo(current, db)

    # Update the database with the new contact times
    for contact in updated_contact_times:
        db.merge(contact)

    db.commit()


def schedule_rf(request: RFTimeRequestModel, db: Session):
    with db as db:
        # Map the request to an RFTime object
        rf_time: RFTime = _map_rftime_model_to_object(request, db)
        schedule(rf_time, db)


def schedule_contact(request: ContactRequestModel, db: Session):
    with db as db:
        # Map the request to an RFTime object
        contact: Contact = _map_contact_model_to_object(request, db)
        schedule(contact, db)


def algo(reqs: List[GeneralContact], db: Session) -> List[GeneralContact]:
    bookings: List[GeneralContact] = []

    requests: List[GeneralContact] = deepcopy(reqs)
    req: GeneralContact
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

    slots = get_slots(requests, db)

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
                        req.set_time_remaining(int(slot.dur))
                        req.decrease_pass()

                        if req.timeRemaining <= 0:
                            requests.remove(req)  # remove from the list of requests
                        break
    return bookings


def get_slots(requests: List[GeneralContact], db: Session) -> List[Visibility]:
    # integrate with gs_mock to filter out unavailable times
    return get_visibilities(requests=requests, db=db)


def get_satellites(db: Session) -> Dict[str, Satellite]:
    satellites: List[Satellite] = list(db.exec(select(Satellite)).all())
    return {str(sat.id): sat for sat in satellites}


def get_ground_stations(db: Session) -> List[GroundStation]:
    return list(db.exec(select(GroundStation)).all())


def get_visibilities(requests: List[GeneralContact], db: Session) -> List[Visibility]:
    """
    Get the availability windows for the all the requests in the list
    Return list of Visibility objects
    """
    ts = load.timescale()

    # in a final implementation ground station (gss) list needs to be retrieved from the DB
    satellites: Dict[str, Satellite] = get_satellites(db)
    # determine the lower and higher time bound for visibility search
    lowest = datetime.strptime("9999-01-01T00:00:00", time_format)
    highest = datetime.strptime("1900-01-01T00:00:00", time_format)

    visibilities: List[Visibility] = []

    # for the request of type Contact, for now we assume that aos and los parameters will comply with GSs station mask
    for req in requests:
        if isinstance(req, RFTime):
            lowest = min(req.start_time, lowest)
            highest = max(req.end_time, highest)
        else:
            r: Contact = req
            lowest = min(req.aos, lowest)
            highest = max(req.los, highest)

        satellites[req.satellite.name] = req.satellite

    static_ground_stations: List[GroundStation] = get_ground_stations(db)
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


def _map_rftime_model_to_object(req: RFTimeRequestModel, db: Session) -> RFTime:
    static_satellites: Dict[str, Satellite] = get_satellites(db)
    sat = get_satellite_by_id(req.satelliteId, static_satellites)

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


def get_satellite_by_id(
    satellite_id: str, satellites: Dict[str, Satellite]
) -> Satellite:
    sat = satellites.get(satellite_id)
    if sat is None:
        raise ValueError(
            f"Satellite {satellite_id} does not exist in the static map.: {satellites}"
        )
    return sat


def get_ground_station_by_name(
    station_name: str, ground_stations: List[GroundStation]
) -> GroundStation:
    for station in ground_stations:
        if station.name == station_name:
            return station
    raise ValueError(f"Ground Station {station_name} does not exist in the static map.")


def _map_contact_model_to_object(req: ContactRequestModel, db: Session) -> Contact:
    static_satellites: Dict[str, Satellite] = get_satellites(db)
    static_ground_stations = get_ground_stations(db)
    sat = get_satellite_by_id(req.satelliteId, static_satellites)
    gs = get_ground_station_by_name(req.location, static_ground_stations)

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
