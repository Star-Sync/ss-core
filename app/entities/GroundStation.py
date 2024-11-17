from skyfield.api import wgs84
from skyfield.toposlib import GeographicPosition

class GroundStation():
    """
    TODO:
    - there should be 2 values of mask parameter: Receive and Send; for now it's the same
    """
    def __init__(self, name: str, lat: float, lon: float, height: float, mask: int, uplink: float, downlink: float, science: float):
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