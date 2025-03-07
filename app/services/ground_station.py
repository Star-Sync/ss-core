from fastapi import HTTPException
from sqlmodel import select, Session
from app.entities.ExclusionCone import ExclusionCone
from app.models.ground_station import GroundStationModel, GroundStationCreateModel
from app.entities.GroundStation import GroundStation


class GroundStationService:
    @staticmethod
    def create_ground_station(db: Session, ground_station: GroundStationCreateModel):
        gs = GroundStation(**ground_station.model_dump())
        db.add(gs)
        db.commit()
        db.refresh(gs)
        return gs

    @staticmethod
    def update_ground_station(db: Session, ground_station: GroundStationModel):
        statement = select(GroundStation).where(GroundStation.id == ground_station.id)
        existing_gs = db.exec(statement).first()
        if existing_gs:
            for key, value in ground_station.model_dump().items():
                setattr(existing_gs, key, value)
            db.commit()
            db.refresh(existing_gs)
            return existing_gs
        else:
            create_model = GroundStationCreateModel(**ground_station.model_dump())
            return GroundStationService.create_ground_station(db, create_model)

    @staticmethod
    def get_ground_stations(db: Session):
        statement = select(GroundStation)
        return db.exec(statement).all()

    @staticmethod
    def get_ground_station(db: Session, gs_id: int):
        statement = select(GroundStation).where(GroundStation.id == gs_id)
        return db.exec(statement).first()

    @staticmethod
    def delete_ground_station(db: Session, gs_id: int):
        statement_gs = select(GroundStation).where(GroundStation.id == gs_id)
        ground_station = db.exec(statement_gs).first()

        if ground_station:
            statement_ex = select(ExclusionCone).where(ExclusionCone.gs_id == gs_id)
            ex_cones = db.exec(statement_ex).all()

            if len(ex_cones) > 0:
                raise HTTPException(
                    status_code=409,
                    detail=f"Cannot delete satellite with the following exclusion cones attached: {[str(ex_cone.id) for ex_cone in ex_cones]}",
                )
            db.delete(ground_station)
            db.commit()
            # if need be, we can return the deleted object; for now it's just a success status
            return True
        return False
