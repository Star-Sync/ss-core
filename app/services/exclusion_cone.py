import logging
import uuid
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlmodel import Sequence, select, Session
from app.models.exclusion_cone import (
    ExclusionConeCreateModel,
    ExclusionConeUpdateModel,
)
from app.entities.ExclusionCone import ExclusionCone
from app.models.user import UserModel
from app.services.ground_station import GroundStationService
from app.services.permissions import (
    Action,
    check_action,
    check_mission_access,
    has_system_privileges,
)
from app.services.satellite import SatelliteService

logger = logging.getLogger(__name__)


class ExclusionConeService:
    @staticmethod
    def create_exclusion_cone(
        db: Session, user: UserModel, exclusion_cone: ExclusionConeCreateModel
    ) -> ExclusionCone:
        try:
            check_action(user, Action.WRITE)
            check_mission_access(user, exclusion_cone.mission)

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
        db: Session,
        user: UserModel,
        ex_cone_id: uuid.UUID,
        exclusion_cone: ExclusionConeUpdateModel,
    ) -> ExclusionCone:
        try:
            check_action(user, Action.WRITE)

            existing_ex_cone = ExclusionConeService.get_exclusion_cone(
                db, user, ex_cone_id
            )

            if not existing_ex_cone:
                raise HTTPException(
                    status_code=404,
                    detail=f"Exclusion cone with ID {ex_cone_id} not found",
                )

            logger.info(
                f"Checking permissions of user ID:{user.id} for updating exclusion cone with ID {ex_cone_id}"
            )
            check_mission_access(user, existing_ex_cone.mission)

            update_data = exclusion_cone.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key == "satellite_id":
                    logger.info(f"Checking if satellite ID:{update_data[key]} exists")
                    SatelliteService.get_satellite(db, update_data[key])
                if key == "gs_id":
                    logger.info(
                        f"Checking if ground station ID:{update_data[key]} exists"
                    )
                    GroundStationService.get_ground_station(db, update_data[key])
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
                detail=f"Database error while updating exclusion cone {ex_cone_id}: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while updating exclusion cone {ex_cone_id}: {str(e)}",
            )

    @staticmethod
    def get_exclusion_cones(db: Session, user: UserModel) -> list[ExclusionCone]:
        try:
            statement = select(ExclusionCone)

            if not has_system_privileges(user):
                statement = select(ExclusionCone).where(
                    (ExclusionCone.mission.in_(user.mission_access))  # type: ignore
                )

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
    def get_exclusion_cone(
        db: Session, user: UserModel, ex_cone_id: uuid.UUID
    ) -> ExclusionCone:
        try:
            check_action(user, Action.READ)

            statement = select(ExclusionCone).where(ExclusionCone.id == ex_cone_id)
            ex_cone = db.exec(statement).first()

            if not ex_cone:
                raise HTTPException(
                    status_code=404,
                    detail=f"Exclusion cone with ID {ex_cone_id} not found",
                )
            check_mission_access(user, ex_cone.mission)
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
    def delete_exclusion_cone(
        db: Session, user: UserModel, ex_cone_id: uuid.UUID
    ) -> ExclusionCone:
        try:
            check_action(user, Action.WRITE)
            exclusion_cone = ExclusionConeService.get_exclusion_cone(
                db, user, ex_cone_id
            )

            if not exclusion_cone:
                raise HTTPException(
                    status_code=404,
                    detail=f"Exclusion cone with ID {ex_cone_id} not found",
                )

            logger.info(
                f"Checking permissions of user ID:{user.id} for deleting exclusion cone with ID {ex_cone_id}"
            )
            check_mission_access(user, exclusion_cone.mission)

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
