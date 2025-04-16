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
from app.entities.Satellite import Satellite
from app.entities.GroundStation import GroundStation
from app.entities.Request import RFRequest, ContactRequest
from app.models.request import ContactRequestModel, RFTimeRequestModel
from app.services.station_sim import StationSimulatorService
import uuid
import logging
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

logger = logging.getLogger(__name__)

random.seed(42)

# Initialize station simulator service
station_sim_service = StationSimulatorService()


@dataclass
class Slot:
    start_time: datetime.datetime
    end_time: datetime.datetime


@dataclass
class Booking:
    slot: Slot
    gs_id: int
    request_id: uuid.UUID
    id: uuid.UUID


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


def check_station_availability(
    station_name: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    desired_state: str,
) -> bool:
    """
    Check if a station is available for scheduling during the given time period.

    Args:
        station_name: Name of the ground station
        start_time: Start time of the requested slot
        end_time: End time of the requested slot
        desired_state: The desired state for the station ("free", "both_busy", "science_busy", "telemetry_busy")

    Returns:
        bool: True if the station is available, False otherwise
    """
    try:
        # Check if the station is free during the requested time
        busy_times = station_sim_service.query_busy_times(
            station=station_name, start_time=start_time, end_time=end_time
        )

        # If there are any busy times that overlap with our requested slot, the station is not available
        for busy_time in busy_times:
            busy_start = datetime.datetime.fromisoformat(busy_time["start_time"])
            busy_end = datetime.datetime.fromisoformat(busy_time["end_time"])

            # Check for overlap
            if start_time < busy_end and end_time > busy_start:
                return False

        return True
    except Exception as e:
        logger.error(f"Error checking station availability: {str(e)}")
        # If we can't check the station simulator, assume the station is available
        return True


def schedule_with_slots(
    requests: list[Request], stations: list[GroundStation]
) -> list[Booking]:
    """Schedule the requests with the given slots

    Args:
        requests (list[Request]): List of requests to schedule
        stations (list[GroundStation]): List of GroundStations to schedule the requests with

    Returns:
        list[Booking]: List of bookings that were scheduled
    """
    slots: dict[str, dict[tuple[datetime.datetime, datetime.datetime], Booking]] = (
        defaultdict(dict)
    )
    bookings: list[Booking] = []
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
                station = next(
                    (s for s in stations if s.id == request.ground_station_id), None
                )

                if not station:
                    logger.error(f"Station not found: {request.ground_station_id}")
                    continue

                # Check if the slot is already taken
                if (start, start + slot_duration) in slots[station_id]:
                    continue

                # Check station simulator availability
                if not check_station_availability(
                    station_name=station.name,
                    start_time=start_time,
                    end_time=end_time,
                    desired_state=(
                        "both_busy"
                        if request.science and request.telemetry
                        else "science_busy" if request.science else "telemetry_busy"
                    ),
                ):
                    continue

                booking = Booking(
                    slot=Slot(start_time=start_time, end_time=end_time),
                    request_id=request.id,
                    gs_id=request.ground_station_id,
                    id=uuid.uuid4(),
                )

                slots[station_id][(start, start + slot_duration)] = booking
                bookings.append(booking)
                # converting from float to int could cause issues in the future
                remaining_time -= int(slot_duration.total_seconds())
                request.scheduled = True

            if not request.scheduled:
                logger.warning(
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
                    request.scheduled = True
                    break

                slot_duration = end - start
                start_time = start
                end_time = end
                for gs in stations:
                    station_name = gs.name
                    if (start, end) not in slots[station_name]:
                        # Check station simulator availability
                        if not check_station_availability(
                            station_name=station_name,
                            start_time=start_time,
                            end_time=end_time,
                            desired_state=(
                                "both_busy"
                                if request.science_time_requested > 0
                                else "telemetry_busy"
                            ),
                        ):
                            continue

                        request.ground_station_id = gs.id
                        booking = Booking(
                            request_id=request.id,
                            slot=Slot(
                                start_time=start_time,
                                end_time=end_time,
                            ),
                            gs_id=gs.id,
                            id=uuid.uuid4(),
                        )

                        slots[station_name][(start, end)] = booking
                        bookings.append(booking)
                        # converting from float to int could cause issues in the future
                        remaining_time -= int((end - start).total_seconds())
                if request.scheduled:
                    break
            if not request.scheduled:
                logger.warning(
                    f"Could not schedule request: {request.mission} - {request.satellite_id}"
                )
    return bookings


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
    def get_rf_time_request(db: Session, request_id: UUID) -> RFRequest | None:
        try:
            req = db.exec(select(RFRequest).where(RFRequest.id == request_id)).first()
            if req is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"RF Time Request with ID {request_id} not found",
                )
            return req
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error getting RF time request: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Database error while getting RF time request: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error getting RF time request: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error getting RF time request: {str(e)}",
            )

    @staticmethod
    def get_contact_request(db: Session, request_id: UUID) -> ContactRequest | None:
        try:
            req = db.exec(
                select(ContactRequest).where(ContactRequest.id == request_id)
            ).first()
            if req is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Contact Request with ID {request_id} not found",
                )
            return req
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error getting contact request: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Database error while getting contact request: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error getting contact request: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error getting contact request: {str(e)}",
            )

    @staticmethod
    def create_rf_request(db: Session, request: RFTimeRequestModel) -> RFRequest:
        try:
            # Validate request data
            if not request.missionName:
                raise HTTPException(
                    status_code=400,
                    detail="Mission name cannot be empty",
                )
            if request.startTime >= request.endTime:
                raise HTTPException(
                    status_code=400,
                    detail="Start time must be before end time",
                )
            if (
                request.uplinkTime < 0
                or request.downlinkTime < 0
                or request.scienceTime < 0
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Time requests cannot be negative",
                )
            if request.minimumNumberOfPasses is None:
                request.minimumNumberOfPasses = 1
            if request.minimumNumberOfPasses < 1:
                raise HTTPException(
                    status_code=400,
                    detail="Minimum number of passes must be at least 1",
                )

            # Map the request model fields to entity fields
            rf_request = RFRequest(
                mission=request.missionName,
                satellite_id=request.satelliteId,
                start_time=request.startTime,
                end_time=request.endTime,
                uplink_time_requested=request.uplinkTime,
                downlink_time_requested=request.downlinkTime,
                science_time_requested=request.scienceTime,
                min_passes=request.minimumNumberOfPasses or 1,
                priority=1,
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
            db.add(rf_request)
            db.commit()
            db.refresh(rf_request)
            return rf_request
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating RF request: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Database error while creating RF request: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error creating RF request: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating RF request: {str(e)}",
            )

    @staticmethod
    def create_contact_request(
        db: Session, request: ContactRequestModel
    ) -> ContactRequest:
        try:
            # Validate request data
            if not request.missionName:
                raise HTTPException(
                    status_code=400,
                    detail="Mission name cannot be empty",
                )
            if request.aosTime >= request.losTime:
                raise HTTPException(
                    status_code=400,
                    detail="AOS time must be before LOS time",
                )
            if request.rfOnTime >= request.rfOffTime:
                raise HTTPException(
                    status_code=400,
                    detail="RF on time must be before RF off time",
                )

            # Map the request model fields to entity fields
            contact_request = ContactRequest(
                mission=request.missionName,
                satellite_id=request.satelliteId,
                start_time=request.aosTime,  # Use AOS time as start time
                end_time=request.losTime,  # Use LOS time as end time
                ground_station_id=request.station_id,
                orbit=request.orbit,
                uplink=request.uplink,
                telemetry=request.telemetry,
                science=request.science,
                aos=request.aosTime,
                los=request.losTime,
                rf_on=request.rfOnTime,
                rf_off=request.rfOffTime,
                duration=int((request.losTime - request.aosTime).total_seconds()),
                priority=1,
                booking_id=None,  # Will be set when scheduled
                scheduled=False,
            )
            db.add(contact_request)
            db.commit()
            db.refresh(contact_request)
            return contact_request
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating contact request: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Database error while creating contact request: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error creating contact request: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating contact request: {str(e)}",
            )

    @staticmethod
    def update_rf_request(db: Session, request: RFTimeRequestModel) -> RFRequest:
        try:
            rf_request = RFRequest(**request.model_dump())
            db.add(rf_request)
            db.commit()
            db.refresh(rf_request)
            return rf_request
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating RF request: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Database error while updating RF request: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error updating RF request: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error updating RF request: {str(e)}",
            )

    @staticmethod
    def delete_rf_time_request(db: Session, request_id: UUID) -> None:
        try:
            request = db.exec(
                select(RFRequest).where(RFRequest.id == request_id)
            ).first()
            if request is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"RF Time Request with ID {request_id} not found",
                )
            db.delete(request)
            db.commit()
            return None
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting RF request: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Database error while deleting RF request: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error deleting RF request: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting RF request: {str(e)}",
            )

    @staticmethod
    def delete_contact_request(db: Session, request_id: UUID) -> None:
        try:
            request = db.exec(
                select(ContactRequest).where(ContactRequest.id == request_id)
            ).first()
            if request is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Contact Request with ID {request_id} not found",
                )
            db.delete(request)
            db.commit()
            return None
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting contact request: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Database error while deleting contact request: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error deleting contact request: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting contact request: {str(e)}",
            )

    @staticmethod
    def get_all_transformed_requests(db: Session) -> list[GeneralContactResponseModel]:
        try:
            rf_requests: list[RFRequest] = list(db.exec(select(RFRequest)).all())
            c_requests: list[ContactRequest] = list(
                db.exec(select(ContactRequest)).all()
            )
            contacts: list[GeneralContactResponseModel] = []
            all_requests: list[Request] = [*rf_requests, *c_requests]
            for request in all_requests:
                result = RequestService.transform_request_to_general(db, request)
                if result is not None:
                    contacts.append(result)
            return contacts
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error getting all transformed requests: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting all transformed requests: {str(e)}")
            raise

    @staticmethod
    def get_all_requests(db: Session) -> list[Request]:
        try:
            rf_requests: list[RFRequest] = list(db.exec(select(RFRequest)).all())
            c_requests: list[ContactRequest] = list(
                db.exec(select(ContactRequest)).all()
            )
            return [*rf_requests, *c_requests]
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error getting all requests: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Database error while getting all requests: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error getting all requests: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error getting all requests: {str(e)}",
            )

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
                raise HTTPException(
                    status_code=404,
                    detail=f"Ground Station with ID {request.ground_station_id} not found",
                )

        sat = SatelliteService.get_satellite(db, request.satellite_id)
        if sat is None:
            logger.error(f"Satellite with ID {request.satellite_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Satellite with ID {request.satellite_id} not found",
            )

        return GeneralContactResponseModel(
            requestType="RFTime" if isinstance(request, RFRequest) else "Contact",
            id=request.id,
            mission=request.mission,
            satellite_name=sat.name,
            station_id=(
                -1 if request.ground_station_id is None else request.ground_station_id
            ),
            uplink=request.uplink if isinstance(request, ContactRequest) else 0,
            telemetry=(request.telemetry if isinstance(request, ContactRequest) else 0),
            science=request.science if isinstance(request, ContactRequest) else 0,
            startTime=request.start_time,
            endTime=request.end_time,
            duration=((request.end_time - request.start_time).total_seconds()),
            aos=request.aos if isinstance(request, ContactRequest) else None,
            rf_on=request.rf_on if isinstance(request, ContactRequest) else None,
            rf_off=request.rf_off if isinstance(request, ContactRequest) else None,
            los=request.los if isinstance(request, ContactRequest) else None,
            orbit=request.orbit if isinstance(request, ContactRequest) else None,
        )

    @staticmethod
    def get_bookings(db: Session) -> list[Booking]:
        # get all requests and schedule them
        try:
            requests = RequestService.get_all_requests(db)
            bookings = schedule_with_slots(
                requests,
                list(GroundStationService.get_ground_stations(db)),
            )
            return bookings
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error getting bookings: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Database error while getting bookings: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error getting bookings: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error getting bookings: {str(e)}",
            )

    @staticmethod
    def sample(
        db: Session,
    ) -> list[GeneralContactResponseModel]:
        sats = SatelliteService.get_satellites(db)
        stations = GroundStationService.get_ground_stations(db)
        if len(sats) < 2 or len(stations) < 2:
            logger.error("Need at least 2 satellites and 2 ground stations to demo")
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 satellites and 2 ground stations to demo",
            )
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
                num_passes_remaining=1,  # Set explicit integer value
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
                num_passes_remaining=1,  # Set explicit integer value
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
                aos=datetime.datetime(2025, 1, 1, 0, 0, 0),
                los=datetime.datetime(2025, 1, 1, 1, 0, 0),
                rf_on=datetime.datetime(2025, 1, 1, 0, 0, 0),
                rf_off=datetime.datetime(2025, 1, 1, 1, 0, 0),
                duration=30,
                priority=1,
                booking_id=None,
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
                aos=datetime.datetime(2025, 1, 1, 0, 0, 0),
                los=datetime.datetime(2025, 1, 1, 1, 0, 0),
                rf_on=datetime.datetime(2025, 1, 1, 0, 0, 0),
                rf_off=datetime.datetime(2025, 1, 1, 1, 0, 0),
                duration=30,
                priority=1,
                booking_id=None,
            ),
        ]
        contacts = []
        # commit requests to db
        for request in requests:
            db.add(request)
        db.commit()
        for request in requests:
            result = RequestService.transform_request_to_general(db, request)
            if result is not None:
                contacts.append(result)
        return contacts
