from skyfield.api import wgs84
from skyfield.toposlib import GeographicPosition
from skyfield.api import wgs84
from skyfield.toposlib import GeographicPosition
from sqlmodel import SQLModel, Field
from typing import Optional


class GroundStation(SQLModel, table=True):  # type: ignore
    __tablename__: str = "ground_stations"  # type: ignore

    """
    TODO:
    - there should be 2 values of mask parameter: Receive and Send; for now it's the same
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str
    lat: float
    lon: float
    height: float
    mask: int
    uplink: float
    downlink: float
    science: float

    # def __init__(
    #     self,
    #     id: Optional[int] = None,
    #     name: str = "",
    #     lat: float = 0,
    #     lon: float = 0,
    #     height: float = 0,
    #     mask: int = 0,
    #     uplink: float = 0,
    #     downlink: float = 0,
    #     science: float = 0,
    # ):
    #     self.id = id
    #     self.name = name
    #     self.lat = lat
    #     self.lon = lon
    #     self.height = height
    #     self.mask = mask
    #     self.uplink = uplink
    #     self.downlink = downlink
    #     self.science = science

    def get_sf_geo_position(self) -> GeographicPosition:
        return wgs84.latlon(
            latitude_degrees=self.lat,
            longitude_degrees=self.lon,
            elevation_m=self.height,
        )

    def __repr__(self):
        return f"GroundStation(name={self.name})"
