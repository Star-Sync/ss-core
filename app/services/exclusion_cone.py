import uuid
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from fastapi import HTTPException
from sqlmodel import select, Session
from app.models.exclusion_cone import (
    ExclusionConeModel,
    ExclusionConeCreateModel,
    ExclusionConeUpdateModel,
)
from app.entities.ExclusionCone import ExclusionCone
from app.services.satellite import SatelliteService


class ExclusionConeService:
    @staticmethod
    def create_exclusion_cone(
        db: Session, exclusion_cone: ExclusionConeCreateModel
    ) -> ExclusionConeModel:
        try:
            # Check if satellite_id exists first
            SatelliteService.get_satellite(
                db, exclusion_cone.satellite_id
            )  # Raises 404 if not found

            # TODO: Check if ground station exists

            ex_cone = ExclusionCone(**exclusion_cone.model_dump())
            db.add(ex_cone)
            db.commit()
            db.refresh(ex_cone)
            return ExclusionConeModel.model_validate(ex_cone)

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
    ) -> ExclusionConeModel:
        try:
            statement = select(ExclusionCone).where(ExclusionCone.id == cone_id)
            existing_ex_cone = db.exec(statement).first()
            if not existing_ex_cone:
                raise HTTPException(
                    status_code=404,
                    detail=f"Exclusion cone with ID {cone_id} not found",
                )

            update_data = exclusion_cone.model_dump(exclude_unset=True)

            # TODO: If user modified satellite or ground station ids, check that corresponding entities exists

            for key, value in update_data.items():
                setattr(existing_ex_cone, key, value)

            db.commit()
            db.refresh(existing_ex_cone)

            return ExclusionConeModel.model_validate(existing_ex_cone)

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
    def get_exclusion_cones(db: Session) -> list[ExclusionConeModel]:
        try:
            statement = select(ExclusionCone)
            ex_cones = db.exec(statement).all()
            return [ExclusionConeModel.model_validate(ec) for ec in ex_cones]

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
    def get_exclusion_cone(db: Session, ex_cone_id: uuid.UUID) -> ExclusionConeModel:
        try:
            statement = select(ExclusionCone).where(ExclusionCone.id == ex_cone_id)
            ex_cone = db.exec(statement).first()
            if not ex_cone:
                raise HTTPException(
                    status_code=404,
                    detail=f"Exclusion cone with ID {ex_cone_id} not found",
                )
            return ExclusionConeModel.model_validate(ex_cone)

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
    def delete_exclusion_cone(db: Session, ex_cone_id: uuid.UUID) -> ExclusionConeModel:
        try:
            statement = select(ExclusionCone).where(ExclusionCone.id == ex_cone_id)
            exclusion_cone = db.exec(statement).first()
            if not exclusion_cone:
                raise HTTPException(
                    status_code=404,
                    detail=f"Exclusion cone with ID {ex_cone_id} not found",
                )
            deleted_ex_cone = ExclusionConeModel.model_validate(exclusion_cone)
            db.delete(exclusion_cone)
            db.commit()

            return deleted_ex_cone

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
