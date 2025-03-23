from collections import defaultdict
from dataclasses import dataclass
import datetime
from pprint import pprint
import random
import numpy as np
from skyfield.api import EarthSatellite, load, Timescale, Time
from skyfield.toposlib import GeographicPosition
from sqlmodel import select, Session
from app.models.request import GeneralContactResponseModel
from app.services.ground_station import GroundStationService
from app.services.satellite import SatelliteService
from ..entities.Satellite import Satellite
from ..entities.GroundStation import GroundStation
from ..entities.Request import RFRequest, ContactRequest
from ..models.request import ContactRequestModel, RFTimeRequestModel
import uuid
import logging
from uuid import UUID


logger = logging.getLogger(__name__)

random.seed(42)


@dataclass
class Slot:
    start_time: datetime.datetime
    end_time: datetime.datetime


@dataclass
class Contact:
    slot: Slot
    request_id: uuid.UUID
    id: uuid.UUID = uuid.uuid4()


Request = RFRequest | ContactRequest
# we have to take in a list of requests and generate a list of contacts
# the goal is to maximize the number of contacts we can make
# we can only make a contact if it is within the time window of the request


def divide_into_slots(
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    slot_duration: int = 15 * 60,
):
    """Divide the time between start_time and end_time into slots of slot_duration

    Args:
        start_time (datetime.datetime): Start time of the time window
        end_time (datetime.datetime): End time of the time window
        slot_duration (int, optional): The length of each slot in seconds. Defaults to 15*60. 15 minutes.

    Returns:
        list[tuple[datetime.datetime, datetime.datetime]]: List of tuples representing the start and end time
    """
    slots: list[tuple[datetime.datetime, datetime.datetime]] = []
    current_time = start_time
    while current_time < end_time:
        slots.append(
            (current_time, current_time + datetime.timedelta(seconds=slot_duration))
        )
        current_time += datetime.timedelta(seconds=slot_duration)

    return slots


def schedule_with_slots(
    requests: list[Request], stations: list[GroundStation]
) -> list[Contact]:
    """Schedule the requests with the given slots

    Args:
        requests (list[Request]): List of requests to schedule
        stations (list[GroundStation]): List of GroundStations to schedule the requests with

    Returns:
        list[Contact]: List of contacts that were scheduled
    """
    slots: dict[str, dict[tuple[datetime.datetime, datetime.datetime], Contact]] = (
        defaultdict(dict)
    )
    contacts: list[Contact] = []
    # sort the requests by earliest end time
    requests.sort(key=lambda r: r.end_time)
    # set all requests to not scheduled
    for request in requests:
        request.scheduled = False

    # Schedule ContactRequests first
    for request in requests:
        if isinstance(request, ContactRequest):
            remaining_time: int = request.duration
            request_slots = divide_into_slots(request.start_time, request.end_time)
            for start, end in request_slots:
                if remaining_time <= 0:
                    break

                slot_duration: datetime.timedelta = min(
                    end - start, datetime.timedelta(seconds=remaining_time)
                )
                start_time = start
                end_time = start_time + slot_duration

                station_id = str(request.ground_station_id)

                if (start, start + slot_duration) in slots[station_id]:
                    continue

                contact = Contact(
                    slot=Slot(start_time=start_time, end_time=end_time),
                    request_id=request.id,
                )

                slots[station_id][(start, start + slot_duration)] = contact
                contacts.append(contact)
                # converting from float to int could cause issues in the future
                remaining_time -= int(slot_duration.total_seconds())
                request.scheduled = True

            if not request.scheduled:
                print(
                    f"Could not schedule request: {request.mission} - {request.satellite_id} - {request.ground_station_id}"
                )

    # Schedule RFRequests next
    for request in requests:
        if isinstance(request, RFRequest):
            request_slots = divide_into_slots(request.start_time, request.end_time)
            remaining_time = max(
                [
                    request.downlink_time_requested,
                    request.uplink_time_requested,
                    request.science_time_requested,
                ]
            )
            for start, end in request_slots:
                if remaining_time <= 0:
                    break

                slot_duration = end - start
                start_time = start
                end_time = end
                for gs in stations:
                    station_name = gs.name
                    if (start, end) not in slots[station_name]:
                        request.ground_station_id = gs.id
                        contact = Contact(
                            request_id=request.id,
                            slot=Slot(
                                start_time=start_time,
                                end_time=end_time,
                            ),
                        )

                        slots[station_name][(start, end)] = contact
                        contacts.append(contact)
                        # converting from float to int could cause issues in the future
                        remaining_time -= int((end - start).total_seconds())
                        request.scheduled = True
                        break
                if request.scheduled:
                    break
            if not request.scheduled:
                print(
                    f"Could not schedule request: {request.mission} - {request.satellite_id}"
                )
    pprint(requests)
    return contacts


def angle_diff(
    start_t: datetime.datetime,
    end_t: datetime.datetime,
    sat1: EarthSatellite,
    sat2: EarthSatellite,
    gs: GeographicPosition,
) -> list[tuple[datetime.datetime, float]]:
    """Calculate the angle difference between two satellites in a given time window

    Args:
        start_t (datetime.datetime): Start time of the time window
        end_t (datetime.datetime): End time of the time window
        sat1 (EarthSatellite): First satellite
        sat2 (EarthSatellite): Second satellite
        gs (GeographicPosition): Geographic position of the ground GroundStation

    Returns:
        list[tuple[datetime.datetime, float]]: List of tuples containing the time and angle difference between the two satellites
    """

    total_mins = int((end_t - start_t).total_seconds() / 60)

    ts = load.timescale()
    times = ts.utc(
        start_t.year,
        start_t.month,
        start_t.day,
        start_t.hour,
        start_t.minute + np.arange(total_mins),  # type: ignore
    )

    angles = []
    for t in times:
        sat1_observed = (sat1 - gs).at(t)
        sat2_observed = (sat2 - gs).at(t)

        # altaz command used to check visibility wrt ground GroundStation
        # third field left blank since we don't need distance
        sat1_altitude, _, _ = sat1_observed.altaz()
        sat2_altitude, _, _ = sat2_observed.altaz()

        if sat1_altitude.degrees > 0 and sat2_altitude.degrees > 0:  # type: ignore
            degree_diff = sat1_observed.separation_from(sat2_observed).degrees
            angles.append((t.utc_datetime(), degree_diff))
    return angles


def get_excl_times(
    angle_diff: list[tuple[datetime.datetime, float]], excl_angle: float
) -> list[tuple[datetime.datetime, datetime.datetime]]:
    """Get the exclusion times based on the angle difference between two satellites

    Args:
        angle_diff (list[tuple[datetime.datetime, float]]): List of tuples containing the time and angle difference between the two satellites
        excl_angle (float): The angle difference threshold

    Returns:
        list[tuple[datetime.datetime, datetime.datetime]]: List of tuples containing the start and end time of the exclusion times
    """
    exclusion_times: list[tuple[datetime.datetime, datetime.datetime]] = []
    min = None
    max = None

    for time, angle in angle_diff:
        if angle < excl_angle:
            if min is None:
                min = time
            max = time
        elif min is not None:
            exclusion_times.append((min, max))  # type: ignore
            min = None

    if min is not None:
        exclusion_times.append((min, max))  # type: ignore

    return exclusion_times


def is_visible(
    satellite: EarthSatellite,
    GroundStation: GroundStation,
    time: datetime.datetime,
    visibility_threshold: float = 5.0,
) -> np.bool:
    """Check if the satellite is visible from the ground GroundStation at the given time

    Args:
        satellite (EarthSatellite): Satellite to check visibility for
        GroundStation (GroundStation): Ground GroundStation to check visibility from
        time (datetime.datetime): Time to check visibility at
        visibility_threshold (float, optional): The angle that defines the visiblity (in degrees). Defaults to 5.0.

    Returns:
        np.bool: _description_
    """

    ts = load.timescale()
    time_obj = ts.from_datetime(time)

    # Skyfield Topos object for ground GroundStation
    gs = GroundStation.get_sf_geo_position()

    diff = satellite - gs
    topocentric = diff.at(time_obj)
    altitude, _, _ = topocentric.altaz()

    return altitude.degrees > visibility_threshold  # type: ignore


class RequestService:

    # crud requests
    @staticmethod
    def get_request(db: Session, request_id: uuid.UUID) -> Request | None:
        rf_request = db.exec(
            select(RFRequest).where(RFRequest.id == request_id)
        ).first()
        if rf_request is None:
            c_request = db.exec(
                select(ContactRequest).where(ContactRequest.id == request_id)
            ).first()
        else:
            return rf_request
        if c_request is None:
            logger.error(f"Request with ID {request_id} not found")
        else:
            return c_request
        return None

    @staticmethod
    def get_rf_time_request(db: Session, request_id: UUID) -> RFRequest | None:
        return db.exec(select(RFRequest).where(RFRequest.id == request_id)).first()

    @staticmethod
    def get_contact_request(db: Session, request_id: UUID) -> ContactRequest | None:
        return db.exec(
            select(ContactRequest).where(ContactRequest.id == request_id)
        ).first()

    @staticmethod
    def create_rf_request(db: Session, request: RFTimeRequestModel) -> RFRequest:
        try:
            # Validate request data
            if not request.missionName:
                raise ValueError("Mission name cannot be empty")
            if request.startTime >= request.endTime:
                raise ValueError("Start time must be before end time")
            if (
                request.uplinkTime < 0
                or request.downlinkTime < 0
                or request.scienceTime < 0
            ):
                raise ValueError("Time requests cannot be negative")
            if request.minimumNumberOfPasses is None:
                request.minimumNumberOfPasses = 1
            if request.minimumNumberOfPasses < 1:
                raise ValueError("Minimum number of passes must be at least 1")

            # Map the request model fields to entity fields
            rf_request = RFRequest(
                mission=request.missionName,
                satellite_id=request.satelliteId,
                start_time=request.startTime,
                end_time=request.endTime,
                uplink_time_requested=int(request.uplinkTime),
                downlink_time_requested=int(request.downlinkTime),
                science_time_requested=int(request.scienceTime),
                min_passes=request.minimumNumberOfPasses or 1,
                priority=1,  # Default priority
                ground_station_id=None,  # Will be set by the scheduler
                contact_id=None,  # Will be set when scheduled
                scheduled=False,
                time_remaining=0,  # Will be calculated in __init__
                num_passes_remaining=request.minimumNumberOfPasses or 1,
            )
            # ensure utc timezone
            rf_request.start_time = rf_request.start_time.replace(
                tzinfo=datetime.timezone.utc
            )
            rf_request.end_time = rf_request.end_time.replace(
                tzinfo=datetime.timezone.utc
            )
            print(rf_request.start_time)
            print(rf_request.end_time)
            db.add(rf_request)
            db.commit()
            db.refresh(rf_request)
            return rf_request
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating RF request: {str(e)}")
            raise

    @staticmethod
    def create_contact_request(
        db: Session, request: ContactRequestModel
    ) -> ContactRequest:
        try:
            # Validate request data
            if not request.missionName:
                raise ValueError("Mission name cannot be empty")
            if request.aosTime >= request.losTime:
                raise ValueError("AOS time must be before LOS time")
            if request.rfOnTime >= request.rfOffTime:
                raise ValueError("RF on time must be before RF off time")

            # Map the request model fields to entity fields
            contact_request = ContactRequest(
                mission=request.missionName,
                satellite_id=request.satelliteId,
                start_time=request.aosTime,  # Use AOS time as start time
                end_time=request.losTime,  # Use LOS time as end time
                ground_station_id=None,  # Will be set by the scheduler
                orbit=request.orbit,
                uplink=request.uplink,
                telemetry=request.telemetry,
                science=request.science,
                aos=request.aosTime,
                los=request.losTime,
                rf_on=request.rfOnTime,
                rf_off=request.rfOffTime,
                duration=int((request.losTime - request.aosTime).total_seconds()),
                priority=1,  # Default priority
                contact_id=None,  # Will be set when scheduled
                scheduled=False,
            )
            db.add(contact_request)
            db.commit()
            db.refresh(contact_request)
            return contact_request
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating contact request: {str(e)}")
            raise

    @staticmethod
    def update_rf_request(db: Session, request: RFTimeRequestModel) -> RFRequest:
        rf_request = RFRequest(**request.model_dump())
        db.add(rf_request)
        db.commit()
        db.refresh(rf_request)
        return rf_request

    @staticmethod
    def delete_rf_time_request(db: Session, request_id: UUID) -> None:
        request = db.exec(select(RFRequest).where(RFRequest.id == request_id)).first()
        if request is None:
            logger.error(f"RF Time Request with ID {request_id} not found")
            return
        db.delete(request)
        db.commit()

    @staticmethod
    def delete_contact_request(db: Session, request_id: UUID) -> None:
        request = db.exec(
            select(ContactRequest).where(ContactRequest.id == request_id)
        ).first()
        if request is None:
            logger.error(f"Contact Request with ID {request_id} not found")
            return
        db.delete(request)
        db.commit()

    @staticmethod
    def get_all_requests(db: Session) -> list[GeneralContactResponseModel]:
        rf_requests: list[RFRequest] = list(db.exec(select(RFRequest)).all())
        c_requests: list[ContactRequest] = list(db.exec(select(ContactRequest)).all())
        contacts: list[GeneralContactResponseModel] = []
        all_requests: list[Request] = [*rf_requests, *c_requests]
        for request in all_requests:
            result = RequestService.transform_request_to_general(db, request)
            if result is not None:
                contacts.append(result)
        return contacts

    @staticmethod
    def transform_request_to_general(
        db: Session,
        request: Request,
    ) -> GeneralContactResponseModel | None:
        if request.ground_station_id is None:
            gs = None
        else:
            gs = GroundStationService.get_ground_station(db, request.ground_station_id)
            if gs is None:
                logger.error(
                    f"Ground Station with ID {request.ground_station_id} not found"
                )
                return None

        sat = SatelliteService.get_satellite(db, request.satellite_id)
        if sat is None:
            logger.error(f"Satellite with ID {request.satellite_id} not found")
            return None

        return GeneralContactResponseModel(
            requestType="RFTime" if isinstance(request, RFRequest) else "Contact",
            id=request.id,
            mission=request.mission,
            satellite_name=sat.name,
            station=gs.name if gs is not None else "N/A",
            uplink=request.uplink if isinstance(request, ContactRequest) else 0,
            telemetry=(request.telemetry if isinstance(request, ContactRequest) else 0),
            science=request.science if isinstance(request, ContactRequest) else 0,
            startTime=request.start_time,
            endTime=request.end_time,
            duration=((request.end_time - request.start_time).total_seconds()),
            aos=request.aos if isinstance(request, ContactRequest) else None,
            rf_on=request.rf_on if isinstance(request, ContactRequest) else None,
            rf_off=request.rf_off if isinstance(request, ContactRequest) else None,
            los=request.rf_off if isinstance(request, ContactRequest) else None,
            orbit=request.orbit if isinstance(request, ContactRequest) else None,
        )

    @staticmethod
    def transform_contact_to_general(
        db: Session,
        contacts: list[Contact],
    ) -> list[GeneralContactResponseModel]:
        results: list[GeneralContactResponseModel] = []
        for contact in contacts:
            request = RequestService.get_request(db, contact.request_id)
            if request is None:
                logger.error(f"Request with ID {contact.request_id} not found")
                continue

            result = RequestService.transform_request_to_general(db, request)
            if result is not None:
                # Override the times with contact slot times
                result.startTime = contact.slot.start_time
                result.endTime = contact.slot.end_time
                result.duration = (
                    contact.slot.end_time - contact.slot.start_time
                ).total_seconds()
                results.append(result)

        return results

    @staticmethod
    def sample(
        db: Session,
    ) -> list[GeneralContactResponseModel]:
        sats = SatelliteService.get_satellites(db)
        stations = GroundStationService.get_ground_stations(db)
        if len(sats) < 2 or len(stations) < 2:
            logger.error("Need at least 2 satellites and 2 ground stations to demo")
            raise ValueError("Need at least 2 satellites and 2 ground stations to demo")
        requests: list[Request] = [
            RFRequest(
                mission="Mission 1",
                satellite_id=sats[0].id,
                start_time=datetime.datetime(2025, 3, 1, 0, 0, 0),
                end_time=datetime.datetime(2025, 3, 1, 1, 0, 0),
                uplink_time_requested=30,
                downlink_time_requested=30,
                science_time_requested=30,
                min_passes=1,
                priority=1,
                contact_id=uuid.uuid4(),
            ),
            RFRequest(
                mission="Mission 2",
                satellite_id=sats[1].id,
                start_time=datetime.datetime(2025, 3, 1, 0, 0, 0),
                end_time=datetime.datetime(2025, 3, 1, 1, 0, 0),
                uplink_time_requested=30,
                downlink_time_requested=30,
                science_time_requested=30,
                min_passes=1,
                priority=1,
                contact_id=uuid.uuid4(),
            ),
            ContactRequest(
                mission="Mission 4",
                satellite_id=sats[0].id,
                start_time=datetime.datetime(2025, 1, 1, 0, 0, 0),
                end_time=datetime.datetime(2025, 1, 1, 1, 0, 0),
                ground_station_id=stations[0].id,
                orbit=1,
                uplink=True,
                telemetry=True,
                science=True,
                aos=None,
                los=None,
                rf_on=None,
                rf_off=None,
                duration=30,
                priority=1,
                contact_id=uuid.uuid4(),
            ),
            ContactRequest(
                mission="Mission 5",
                satellite_id=sats[1].id,
                start_time=datetime.datetime(2025, 1, 1, 0, 0, 0),
                end_time=datetime.datetime(2025, 1, 1, 1, 0, 0),
                ground_station_id=stations[1].id,
                orbit=1,
                uplink=True,
                telemetry=True,
                science=True,
                aos=None,
                los=None,
                rf_on=None,
                rf_off=None,
                duration=30,
                priority=1,
                contact_id=uuid.uuid4(),
            ),
        ]
        contacts = []
        for request in requests:
            result = RequestService.transform_request_to_general(db, request)
            if result is not None:
                contacts.append(result)
        return contacts
