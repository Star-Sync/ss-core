from skyfield.sgp4lib import EarthSatellite


class Satellite:
    """
    TODO:
    - have exCone as object instead of string
    """

    def __init__(
        self,
        tle: str,
        uplink: float,
        downlink: float,
        science: float,
        exCone: str,
        priority: int,
    ):
        self.name = tle.splitlines()[0]
        self.tle = tle
        self.uplink = uplink
        self.downlink = downlink
        self.science = science
        self.exCone = exCone
        self.priority = priority

    def get_sf_sat(self) -> EarthSatellite:
        tle_lines = self.tle.splitlines()
        satellite = EarthSatellite(tle_lines[1], tle_lines[2], tle_lines[0])
        return satellite

    def __repr__(self):
        return f"Satellite(name={self.name})"
