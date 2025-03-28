from skyfield.api import wgs84  # type: ignore
from skyfield.toposlib import GeographicPosition  # type: ignore
from sqlmodel import SQLModel, Field


class GroundStation(SQLModel, table=True):  # type: ignore
    __tablename__: str = "ground_stations"  # type: ignore

    """
    TODO:
    - there should be 2 values of mask parameter: Receive and Send; for now it's the same
    """

    id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})
    name: str
    lat: float
    lon: float
    height: float
    mask: int
    uplink: float
    downlink: float
    science: float

    def get_sf_geo_position(self) -> GeographicPosition:
        return wgs84.latlon(
            latitude_degrees=self.lat,
            longitude_degrees=self.lon,
            elevation_m=self.height,
        )

    def __repr__(self):
        return f"GroundStation(id={self.id}, name={self.name})"
