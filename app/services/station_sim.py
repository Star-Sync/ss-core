import requests
from datetime import datetime
from typing import Optional, List, Dict, Any, NoReturn
from fastapi import HTTPException
import logging
import os
from urllib3.exceptions import MaxRetryError, NewConnectionError

logger = logging.getLogger(__name__)


class StationSimulatorService:
    def __init__(self, base_url: Optional[str] = None) -> None:
        """Initialize the station simulator service.

        Args:
            base_url: Optional base URL for the station simulator service.
                     If not provided, will use STATION_SIM_URL environment variable
                     or default to http://station_simulator-state_machines-1:5000
        """
        env_url = os.getenv("STATION_SIM_URL")
        self.base_url = (
            base_url or env_url or "http://station_simulator-state_machines-1:5000"
        ).rstrip("/")
        logger.info(
            f"Initialized StationSimulatorService with base URL: {self.base_url}"
        )

    def _handle_request_error(self, operation: str, error: Exception) -> NoReturn:
        """Handle request errors consistently.

        Args:
            operation: Description of the operation that failed
            error: The exception that occurred
        """
        error_msg = f"Error {operation}: {str(error)}"
        logger.error(error_msg)

        if isinstance(error, (MaxRetryError, NewConnectionError)):
            raise HTTPException(
                status_code=503,
                detail=f"Station simulator service is not available at {self.base_url}. Please ensure the service is running.",
            )
        else:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to {operation} with station simulator: {str(error)}",
            )

    def schedule_pass(
        self,
        station: str,
        start_time: datetime,
        end_time: datetime,
        state: str,
        mission: str,
    ) -> Dict[str, Any]:
        """
        Schedule a pass at a ground station.

        Args:
            station: Name of the ground station (e.g., "Inuvik NorthWest", "Prince Albert", "Gatineau Quebec")
            start_time: Start time of the pass
            end_time: End time of the pass
            state: Desired state ("free", "both_busy", "science_busy", "telemetry_busy")
            mission: Name of the mission

        Returns:
            Dict containing the response from the station simulator
        """
        try:
            url = f"{self.base_url}/{station}/schedule_pass/"
            payload = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "state": state,
                "mission": mission,
            }

            logger.debug(f"Scheduling pass at {url} with payload: {payload}")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            self._handle_request_error("scheduling pass", e)

    def query_state_at(self, station: str, query_time: datetime) -> Dict[str, Any]:
        """
        Query the state of a ground station at a specific time.

        Args:
            station: Name of the ground station
            query_time: Time to query the state at

        Returns:
            Dict containing the state and mission information
        """
        try:
            url = f"{self.base_url}/{station}/query_state_at/{query_time.isoformat()}"
            logger.debug(f"Querying state at {url}")
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            self._handle_request_error("querying state", e)

    def query_busy_times(
        self, station: str, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Query busy times for a ground station within a time range.

        Args:
            station: Name of the ground station
            start_time: Start of the time range
            end_time: End of the time range

        Returns:
            List of Dicts containing busy time information
        """
        try:
            url = f"{self.base_url}/{station}/query_busy_times/"
            params = {
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            logger.debug(f"Querying busy times at {url} with params: {params}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()["busy_times"]

        except Exception as e:
            self._handle_request_error("querying busy times", e)
