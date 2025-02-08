from sqlmodel import select
from app.models.ground_station import GroundStationModel, GroundStationCreateModel
from app.entities.GroundStation import GroundStation
from sqlalchemy.orm import Session


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
        existing_gs = db.execute(statement).scalar_one_or_none()
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
        return db.query(GroundStation).all()

    @staticmethod
    def get_ground_station(db: Session, gs_id: int):
        statement = select(GroundStation).where(GroundStation.id == gs_id)
        return db.exec(statement).first()

    @staticmethod
    def delete_ground_station(db: Session, gs_id: int):
        statement = select(GroundStation).where(GroundStation.id == gs_id)
        ground_station = db.execute(statement).scalar_one_or_none()
        if ground_station:
            db.delete(ground_station)
            db.commit()
            # if need be, we can return the deleted object; for now it's just a success status
            return True
        return False
