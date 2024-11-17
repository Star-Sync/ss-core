import copy
from datetime import datetime
from typing import List
from app.entities import GeneralContact
from skyfield.api import load
from app.entities.Visibility import Visibility
from ..entities.GroundStation import GroundStation
from ..entities.RFTime import RFTime
from ..entities.Satellite import Satellite
from ..entities.GeneralContact import GeneralContact, existing_bookings, lock
from ..models.request import GeneralContactResponseModel, RFTimeRequestModel, ContactRequestModel
from skyfield.api import utc

##################### Set up of static values and objects #####################
time_format = "%Y-%m-%dT%H:%M:%S"

tle1 = '''SCISAT 1
1 27858U 03036A   24298.42572809  .00002329  00000+0  31378-3 0  9994
2 27858  73.9300 283.7690 0006053 131.3701 228.7996 14.79804256142522'''
tle2 = '''NEOSSAT
1 39089U 13009D   24298.50343230  .00000620  00000+0  23091-3 0  9992
2 39089  98.4036 122.5021 0010164 233.8050 126.2197 14.35350046610553'''

static_satellites: dict[str, Satellite] = {
    "SCISAT 1": Satellite(tle1, 150, 150, 150, "exCone", 4),
    "NEOSSAT": Satellite(tle2, 150, 150, 150, "exCone", 4)
}

static_ground_stations: List[GroundStation] = [
    GroundStation("inuvik_northwest", 68.3195, -133.549, 102.5, 0, 150, 150, 150),
    GroundStation("prince_albert", 53.2124, -105.934, 490.3, 0, 150, 150, 150),
    GroundStation("gatineau_quebec", 45.5846, -75.8083, 240.1, 0, 150, 150, 150)
]
###############################################################################

# Might end up using abstract GeneralContactResponseModel class
async def schedule(request: RFTimeRequestModel) -> List[str]:
    
    rf_time: GeneralContact = _map_model_to_object(request)

    async with lock:
        # get the existing bookings 
        global existing_bookings
        current = copy.deepcopy(existing_bookings)

        # add new booking
        current.append(rf_time)
        # perform scheduling
        existing_bookings = algo(current)

        response = [repr(booking) for booking in existing_bookings]

    print(response)

    return response
    

def algo(requests: List[GeneralContact]) -> List[GeneralContact]:
    # in a final implementation ground station (gss) list needs to be retrieved from the DB
    slots = get_slots(reqs=requests, gss=static_ground_stations)

    bookings: List[GeneralContact] = []


    # not the most optimal (probably the most basic algo)
    # does not consider any edge cases (ex. no more room for scheduling)
    for slot in slots:
        for req in requests:
            if req.start_time <= slot.start <= req.end_time and req.start_time <= slot.end <= req.end_time:
                if slot.sat == req.satellite and req.timeRemaining > 0:
                    last = len(bookings)
                    if len(bookings)==0 or slot.start > bookings[last-1].end_time:
                        booking = GeneralContact(
                            mission=req.mission, 
                            satellite=req.satellite, 
                            station=slot.gs, 
                            uplink=req.uplink!=float(0),
                            telemetry=req.telemetry!=float(0),
                            science=req.science!=float(0),
                            start_time=slot.start,
                            end_time=slot.end)
                        bookings.append(booking)

                        # modify the request to decrease the time remaining 
                        # need to modify the logic such that all passes are used
                        req.set_time_remaining(slot.dur)
                        req.passNumRemaining -= 1
                        break
    
    return bookings


def get_slots(reqs: List[RFTime], gss: List[GroundStation]) -> List[Visibility]:
    '''
    Get the availability windows for the all the requests in the list
    Return list of Visibility objects
    '''
    ts = load.timescale()
    
    sats = set()

    lowest = datetime.strptime("9999-01-01T00:00:00", time_format)
    highest = datetime.strptime("1900-01-01T00:00:00", time_format)

    visibilities: List[Visibility] = []
    
    for r in reqs:
        sats.add(r.satellite) 
        lowest = min(r.start_time, lowest)
        highest = max(r.end_time, highest)

    # Three nested for-loops - horrible - I know; will be optimized later
    for s in sats:
        for g in gss:
            t, events = s.get_sf_sat().find_events(g.get_sf_geo_position(), ts.from_datetime(lowest.replace(tzinfo=utc)), ts.from_datetime(highest.replace(tzinfo=utc)), g.mask)
            current_rise = None

            for ti, event in zip(t, events):
                if event == 0:
                    current_rise = ti.utc_datetime().replace(tzinfo=None)
                elif event == 2 and current_rise:
                    visibilities.append(Visibility(gs=g, sat=s, start=current_rise, end=ti.utc_datetime().replace(tzinfo=None)))
                    current_rise = None
    visibilities.sort(key=lambda v: v.start)

    return visibilities


def _map_model_to_object(req: GeneralContactResponseModel) -> RFTime:
    print("req inside mapper", req.satellite)
    sat = static_satellites.get(req.satellite)
    if sat is None:
        raise ValueError(f"Satellite {req.satellite} does not exist in the static map.")

    return RFTime(
        mission=req.mission,
        satellite=sat,
        start_time = req.startTime,
        end_time = req.endTime,
        uplink = req.uplink,
        downlink = req.downlink,
        science = req.science,
        pass_num = req.passNum
    )