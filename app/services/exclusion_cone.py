import uuid
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlmodel import Sequence, select, Session
from app.models.exclusion_cone import (
    ExclusionConeCreateModel,
    ExclusionConeUpdateModel,
)
from app.entities.ExclusionCone import ExclusionCone
from app.services.ground_station import GroundStationService
from app.services.satellite import SatelliteService


class ExclusionConeService:
    @staticmethod
    def create_exclusion_cone(
        db: Session, exclusion_cone: ExclusionConeCreateModel
    ) -> ExclusionCone:
        try:
            # Check if satellite and ground station exist; raise an exception otherwise
            SatelliteService.get_satellite(db, exclusion_cone.satellite_id)
            GroundStationService.get_ground_station(db, exclusion_cone.gs_id)

            ex_cone = ExclusionCone(**exclusion_cone.model_dump())
            db.add(ex_cone)
            db.commit()
            db.refresh(ex_cone)
            return ex_cone

        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=503,
                detail=f"Database error while creating exclusion cone: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while creating exclusion cone: {str(e)}",
            )

    @staticmethod
    def update_exclusion_cone(
        db: Session, cone_id: uuid.UUID, exclusion_cone: ExclusionConeUpdateModel
    ) -> ExclusionCone:
        try:
            existing_ex_cone = ExclusionConeService.get_exclusion_cone(db, cone_id)

            if not existing_ex_cone:
                raise HTTPException(
                    status_code=404,
                    detail=f"Exclusion cone with ID {cone_id} not found",
                )

            update_data = exclusion_cone.model_dump(exclude_unset=True)

            # Check if satellite and ground station exist; raise an exception otherwise
            SatelliteService.get_satellite(db, update_data["satellite_id"])
            GroundStationService.get_ground_station(db, update_data["gs_id"])

            for key, value in update_data.items():
                setattr(existing_ex_cone, key, value)

            db.commit()
            db.refresh(existing_ex_cone)
            return existing_ex_cone

        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=503,
                detail=f"Database error while updating exclusion cone {cone_id}: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while updating exclusion cone {cone_id}: {str(e)}",
            )

    @staticmethod
    def get_exclusion_cones(db: Session) -> list[ExclusionCone]:
        try:
            statement = select(ExclusionCone)
            ex_cones = db.exec(statement).all()
            return list(ex_cones)

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Database error while fetching exclusion cones: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while fetching exclusion cones: {str(e)}",
            )

    @staticmethod
    def get_exclusion_cone(db: Session, ex_cone_id: uuid.UUID) -> ExclusionCone:
        try:
            statement = select(ExclusionCone).where(ExclusionCone.id == ex_cone_id)
            ex_cone = db.exec(statement).first()

            if not ex_cone:
                raise HTTPException(
                    status_code=404,
                    detail=f"Exclusion cone with ID {ex_cone_id} not found",
                )
            return ex_cone

        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Database error while fetching exclusion cone {ex_cone_id}: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while fetching exclusion cone {ex_cone_id}: {str(e)}",
            )

    @staticmethod
    def delete_exclusion_cone(db: Session, ex_cone_id: uuid.UUID) -> ExclusionCone:
        try:
            exclusion_cone = ExclusionConeService.get_exclusion_cone(db, ex_cone_id)

            if not exclusion_cone:
                raise HTTPException(
                    status_code=404,
                    detail=f"Exclusion cone with ID {ex_cone_id} not found",
                )
            db.delete(exclusion_cone)
            db.commit()
            return exclusion_cone

        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=503,
                detail=f"Database error while deleting exclusion cone {ex_cone_id}: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while deleting exclusion cone {ex_cone_id}: {str(e)}",
            )
