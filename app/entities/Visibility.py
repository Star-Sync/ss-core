from datetime import datetime
from app.entities import GroundStation, Satellite


class Visibility:
    def __init__(
        self, gs: GroundStation, sat: Satellite, start: datetime, end: datetime
    ):
        self.gs = gs
        self.sat = sat
        self.start = start
        self.end = end
        self.dur = (self.end - self.start).total_seconds()

    def __repr__(self):
        return (
            f"Visibility(gs={self.gs.name}, sat={self.sat.name}, "
            f"start={self.start}, end={self.end}, dur={self.dur}s)"
        )
