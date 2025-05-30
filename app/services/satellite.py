import uuid
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, Session
from sqlalchemy.orm import joinedload
from app.models.satellite import (
    SatelliteCreateModel,
    SatelliteUpdateModel,
)
from app.entities.Satellite import Satellite


class SatelliteService:
    @staticmethod
    def create_satellite(db: Session, satellite: SatelliteCreateModel) -> Satellite:
        # TODO: Before we service the request in the future we must first validate that request is legitimate (token validation)
        # TODO: Check user permissions to allow satellite creation
        try:
            sat = Satellite(**satellite.model_dump())
            db.add(sat)
            db.commit()
            db.refresh(sat)
            return sat

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=503,
                detail=f"Database error while creating satellite: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while creating satellite: {str(e)}",
            )

    @staticmethod
    def update_satellite(
        db: Session, sat_id: uuid.UUID, satellite: SatelliteUpdateModel
    ) -> Satellite:
        # TODO: Before we service the request in the future we must first validate that request is legitimate (token validation)
        # TODO: Check user permissions to allow update
        try:
            existing_sat = SatelliteService.get_satellite(db, sat_id)

            if not existing_sat:
                raise HTTPException(
                    status_code=404, detail=f"Satellite with ID {sat_id} not found"
                )

            update_data = satellite.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(existing_sat, key, value)

            db.commit()
            db.refresh(existing_sat)
            return existing_sat

        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=503,
                detail=f"Database error while updating satellite {sat_id}: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while updating satellite {sat_id}: {str(e)}",
            )

    @staticmethod
    def get_satellites(db: Session) -> list[Satellite]:
        # TODO: Before we service the request in the future we must first validate that request is legitimate (token validation)
        # TODO: Check user permissions to filter which satellites to return
        try:
            statement = select(Satellite).options(joinedload(Satellite.ex_cones))
            satellites = db.exec(statement).unique().all()
            return list(satellites)

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Database error while fetching satellites: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while fetching satellites: {str(e)}",
            )

    @staticmethod
    def get_satellite(db: Session, sat_id: uuid.UUID) -> Satellite:
        # TODO: Before we service the request in the future we must first validate that request is legitimate (token validation)
        # TODO: Check user permissions to return satellite
        try:
            statement = (
                select(Satellite)
                .where(Satellite.id == sat_id)
                .options(joinedload(Satellite.ex_cones))
            )
            satellite = db.exec(statement).unique().first()

            if satellite is None:
                raise HTTPException(
                    status_code=404, detail=f"Satellite with ID {sat_id} not found"
                )
            return satellite

        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Database error while fetching satellite {sat_id}: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while fetching satellite {sat_id}: {str(e)}",
            )

    @staticmethod
    def delete_satellite(db: Session, sat_id: uuid.UUID) -> Satellite:
        # TODO: Before we service the request in the future we must first validate that request is legitimate (token validation)
        # TODO: Check user permissions to delete satellite
        try:
            satellite = SatelliteService.get_satellite(db, sat_id)

            if not satellite:
                raise HTTPException(
                    status_code=404, detail=f"Satellite with ID {sat_id} not found"
                )

            if len(satellite.ex_cones) > 0:
                raise HTTPException(
                    status_code=409,
                    detail=f"Cannot delete satellite with the following exclusion cones attached: {[str(ex_cone.id) for ex_cone in satellite.ex_cones]}",
                )

            db.delete(satellite)
            db.commit()
            return satellite

        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Database error while deleting satellite {sat_id}: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while deleting satellite {sat_id}: {str(e)}",
            )
