import uuid
from sqlmodel import select, Session
from sqlalchemy.orm import joinedload
from app.models.exclusion_cone import ExclusionConeModel
from app.models.satellite import SatelliteModel, SatelliteCreateModel
from app.entities.Satellite import Satellite


class SatelliteService:
    @staticmethod
    def create_satellite(db: Session, satellite: SatelliteCreateModel):
        sat = Satellite(**satellite.model_dump())
        db.add(sat)
        db.commit()
        db.refresh(sat)
        return sat

    @staticmethod
    def update_satellite(db: Session, satellite: SatelliteModel):
        statement = select(Satellite).where(Satellite.id == satellite.id)
        existing_sat = db.exec(statement).first()
        if existing_sat:
            for key, value in satellite.model_dump().items():
                setattr(existing_sat, key, value)
            db.commit()
            db.refresh(existing_sat)
            return existing_sat
        else:
            create_model = SatelliteCreateModel(**satellite.model_dump())
            return SatelliteService.create_satellite(db, create_model)

    @staticmethod
    def get_satellites(db: Session):
        statement = select(Satellite).options(joinedload(Satellite.ex_cones))
        return db.exec(statement).all()

    @staticmethod
    def get_satellite(db: Session, sat_id: uuid.UUID):
        statement = (
            select(Satellite)
            .where(Satellite.id == sat_id)
            .options(joinedload(Satellite.ex_cones))
        )
        return db.exec(statement).first()

    @staticmethod
    def delete_satellite(db: Session, sat_id: uuid.UUID):
        statement = select(Satellite).where(Satellite.id == sat_id)
        satellite = db.exec(statement).first()
        if satellite:
            db.delete(satellite)
            db.commit()
            # if need be, we can return the deleted object; for now it's just a success status
            return True
        return False
