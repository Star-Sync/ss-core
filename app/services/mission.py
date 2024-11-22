from fastapi import HTTPException
from sqlmodel import Session, select
from ..models.mission import Mission, MissionCreate


def get_mission_by_id(missionid: int, db: Session) -> Mission | None:
    statement = select(Mission).where(Mission.missionid == missionid)
    result = db.exec(statement).first()
    return result


def create_mission_service(mission: MissionCreate, db: Session) -> Mission:
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


def delete_mission_service(missionid: int, db: Session):
    mission = get_mission_by_id(missionid, db)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    db.delete(mission)
    db.commit()
    return {"detail": "Mission deleted successfully"}


def list_missions_service(db: Session):
    statement = select(Mission)
    results = db.exec(statement).all()
    return results
