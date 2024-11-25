from datetime import datetime
from app.entities.GroundStation import GroundStation
from app.entities.Satellite import Satellite
from sqlmodel import Relationship, SQLModel, Field
from typing import Optional


class Visibility(SQLModel, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    gs_id: int = Field(foreign_key="groundstation.id")
    gs: Optional[GroundStation] = Relationship()
    sat_id: int = Field(foreign_key="satellite.id")
    sat: Satellite = Relationship()
    start: datetime
    end: datetime
    dur: float

    def __init__(
        self, gs: GroundStation, sat: Satellite, start: datetime, end: datetime
    ):
        self.gs = gs
        self.sat = sat
        self.start = start
        self.end = end
        self.dur = (self.end - self.start).total_seconds()

    def __repr__(self):
        return f"Visibility(gs={self.gs}, sat={self.sat}, start={self.start}, end={self.end}, dur={self.dur}s)"
