from fastapi import APIRouter
from sqlmodel import Field, Session, SQLModel, create_engine, select

router = APIRouter(
    prefix="/hello",
    tags=["hello"],
)


class Mission(SQLModel, table=True):
    missionid: int | None = Field(default=None, primary_key=True)
    missionname: str = Field(sa_column_kwargs={"nullable": False, "unique": True})


@router.get("/")
def hello():
    # use ..services.db to get a database session
    # and just return a simple message
    from ..services.db import get_db

    # read the tables
    db = next(get_db())

    # create a mission
    mission = Mission(missionname="Mission 1")
    db.add(mission)
    db.commit()
    db.refresh(mission)
    statement = select(Mission)
    results = db.exec(statement)
    for mission in results:
        print(mission)

    return {"message": "Hello, World!"}
