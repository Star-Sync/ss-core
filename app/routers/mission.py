from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..services.db import get_db
from ..models.mission import Mission, MissionCreate

router = APIRouter(
    prefix="/mission",
    tags=["mission"],
)


# Utility function to retrieve a mission by ID
def get_mission_by_id(missionid: int, db: Session) -> Mission | None:
    statement = select(Mission).where(Mission.missionid == missionid)
    result = db.exec(statement).first()
    return result


@router.post("/", response_model=Mission, status_code=201)
def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
    # Check if a mission with the same name already exists
    existing_mission = db.exec(
        select(Mission).where(Mission.missionname == mission.missionname)
    ).first()
    if existing_mission:
        raise HTTPException(
            status_code=400, detail="Mission with this name already exists"
        )
    _mission = Mission.model_validate(mission)

    db.add(_mission)
    db.commit()
    db.refresh(_mission)
    return _mission


@router.delete("/{missionid}", status_code=204)
def delete_mission(missionid: int, db: Session = Depends(get_db)):
    mission = get_mission_by_id(missionid, db)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    db.delete(mission)
    db.commit()
    return {"detail": "Mission deleted successfully"}


@router.get("/", response_model=list[Mission])
def list_missions(db: Session = Depends(get_db)):
    statement = select(Mission)
    results = db.exec(statement).all()
    return results
