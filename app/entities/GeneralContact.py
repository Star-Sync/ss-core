from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
from typing import List, Optional
from app.entities.GroundStation import GroundStation
from app.entities.Satellite import Satellite
from app.models.request import GeneralContactResponseModel


class GeneralContact(ABC):
    def __init__(
        self,
        mission: str,
        satellite: Satellite,
        station: Optional[GroundStation] = GroundStation(),
    ):
        self.mission = mission
        self.satellite = satellite
        self.station = station

    @abstractmethod
    def __repr__(self):
        pass
