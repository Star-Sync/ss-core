from skyfield.api import wgs84
from skyfield.toposlib import GeographicPosition
from skyfield.api import wgs84
from skyfield.toposlib import GeographicPosition
from sqlmodel import Relationship, SQLModel, Field
from typing import TYPE_CHECKING
from app.entities.Contact import Contact
from app.entities.RFTime import RFTime


class GroundStation(SQLModel, table=True):  # type: ignore
    """
    TODO:
    - there should be 2 values of mask parameter: Receive and Send; for now it's the same
    """

    id: int = Field(default=None, primary_key=True)
    name: str
    lat: float
    lon: float
    height: float
    mask: int
    uplink: float
    downlink: float
    science: float
    rf_times: list["RFTime"] = Relationship(
        back_populates="station", sa_relationship_kwargs={"lazy": "immediate"}
    )
    contacts: list["Contact"] = Relationship(
        back_populates="station", sa_relationship_kwargs={"lazy": "immediate"}
    )

    def __init__(
        self,
        name: str = "",
        lat: float = 0,
        lon: float = 0,
        height: float = 0,
        mask: int = 0,
        uplink: float = 0,
        downlink: float = 0,
        science: float = 0,
    ):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.height = height
        self.mask = mask
        self.uplink = uplink
        self.downlink = downlink
        self.science = science

    def get_sf_geo_position(self) -> GeographicPosition:
        return wgs84.latlon(self.lat, self.lon, self.height)

    def __repr__(self):
        return f"GroundStation(name={self.name})"
