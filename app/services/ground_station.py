from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, Session
from app.entities.ExclusionCone import ExclusionCone
from app.models.ground_station import (
    GroundStationModel,
    GroundStationCreateModel,
    GroundStationUpdateModel,
)
from app.entities.GroundStation import GroundStation


class GroundStationService:
    @staticmethod
    def create_ground_station(db: Session, ground_station: GroundStationCreateModel):
        # TODO: Before we service the request in the future we must first validate that request is legitimate (token validation)
        # TODO: Check user permissions to allow satellite creation
        gs = GroundStation(**ground_station.model_dump())
        db.add(gs)
        db.commit()
        db.refresh(gs)
        return gs

    @staticmethod
    def update_ground_station(
        db: Session, gs_id: int, request: GroundStationUpdateModel
    ) -> GroundStationModel:
        try:
            statement = select(GroundStation).where(GroundStation.id == gs_id)
            existing_gs = db.exec(statement).first()

            if not existing_gs:
                raise HTTPException(
                    status_code=404, detail=f"Ground Station with ID {gs_id} not found"
                )

            update_data = request.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(existing_gs, key, value)

            db.commit()
            db.refresh(existing_gs)
            print(existing_gs)
            return GroundStationModel.model_validate(existing_gs)
        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=503,
                detail=f"Database error while updating ground station {gs_id}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while updating ground station {gs_id}: {str(e)}",
            )

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
