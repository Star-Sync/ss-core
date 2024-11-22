from sqlmodel import SQLModel, Field


class MissionBase(SQLModel):
    missionname: str


class Mission(MissionBase, SQLModel, table=True):  # type: ignore
    missionid: int | None = Field(default=None, primary_key=True)


class MissionCreate(MissionBase):
    pass