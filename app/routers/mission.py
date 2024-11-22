from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..services.db import get_db
from ..models.mission import Mission, MissionCreate
from ..services.mission import (
    create_mission_service,
    delete_mission_service,
    list_missions_service,
)

router = APIRouter(
    prefix="/mission",
    tags=["mission"],
)


@router.post("/", response_model=Mission, status_code=201)
def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
    return create_mission_service(mission, db)


@router.delete("/{missionid}", status_code=204)
def delete_mission(missionid: int, db: Session = Depends(get_db)):
    return delete_mission_service(missionid, db)


@router.get("/", response_model=list[Mission])
def list_missions(db: Session = Depends(get_db)):
    return list_missions_service(db)
