from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List, Dict, Any
from app.services.station_sim import StationSimulatorService
from app.routers.error import getErrorResponses

router = APIRouter(prefix="/station-sim", tags=["Station Simulator"])

# Initialize the service
station_sim_service = StationSimulatorService()


@router.post(
    "/{station}/schedule_pass",
    summary="Schedule a pass at a ground station",
    response_model=Dict[str, Any],
    responses={
        503: {"description": "Service Unavailable"},
        500: {"description": "Internal Server Error"},
    },
)
async def schedule_pass(
    station: str, start_time: datetime, end_time: datetime, state: str, mission: str
) -> Dict[str, Any]:
    """
    Schedule a pass at a ground station.

    Args:
        station: Name of the ground station (e.g., "ICAN", "GATN", "PASS")
        start_time: Start time of the pass
        end_time: End time of the pass
        state: Desired state ("free", "both_busy", "science_busy", "telemetry_busy")
        mission: Name of the mission
    """
    return station_sim_service.schedule_pass(
        station=station,
        start_time=start_time,
        end_time=end_time,
        state=state,
        mission=mission,
    )


@router.get(
    "/{station}/query_state_at/{query_time}",
    summary="Query the state of a ground station at a specific time",
    response_model=Dict[str, Any],
    responses={
        503: {"description": "Service Unavailable"},
        500: {"description": "Internal Server Error"},
    },
)
async def query_state_at(station: str, query_time: datetime) -> Dict[str, Any]:
    """
    Query the state of a ground station at a specific time.

    Args:
        station: Name of the ground station
        query_time: Time to query the state at
    """
    return station_sim_service.query_state_at(station=station, query_time=query_time)


@router.get(
    "/{station}/query_busy_times",
    summary="Query busy times for a ground station within a time range",
    response_model=List[Dict[str, Any]],
    responses={
        503: {"description": "Service Unavailable"},
        500: {"description": "Internal Server Error"},
    },
)
async def query_busy_times(
    station: str, start_time: datetime, end_time: datetime
) -> List[Dict[str, Any]]:
    """
    Query busy times for a ground station within a time range.

    Args:
        station: Name of the ground station
        start_time: Start of the time range
        end_time: End of the time range
    """
    return station_sim_service.query_busy_times(
        station=station, start_time=start_time, end_time=end_time
    )
