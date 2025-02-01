from app.models.ground_station import GroundStationModel
from app.entities.GroundStation import GroundStation
from sqlalchemy.orm import Session


class GroundStationService:
    @staticmethod
    def create_ground_station(db: Session, ground_station: GroundStationModel):
        gs = GroundStation(**ground_station.model_dump())
        db.add(gs)
        db.commit()
        db.refresh(gs)
        return gs

    @staticmethod
    def update_ground_station(db: Session, ground_station: GroundStationModel):
        existing_gs = (
            db.query(GroundStation)
            .filter(GroundStation.id == ground_station.id)
            .first()
        )
        if existing_gs:
            for key, value in ground_station.model_dump().items():
                setattr(existing_gs, key, value)
            db.commit()
            db.refresh(existing_gs)
            return existing_gs
        else:
            return GroundStationService.create_ground_station(db, ground_station)

    @staticmethod
    def get_ground_stations(db: Session):
        return db.query(GroundStation).all()

    @staticmethod
    def get_ground_station(db: Session, gs_id: int):
        return db.query(GroundStation).filter(GroundStation.id == gs_id).first()

    @staticmethod
    def delete_ground_station(db: Session, gs_id: int):
        ground_station = (
            db.query(GroundStation).filter(GroundStation.id == gs_id).first()
        )
        if ground_station:
            db.delete(ground_station)
            db.commit()
            return True
        return False
