import uuid
from sqlmodel import select, Session
from app.models.exclusion_cone import ExclusionConeModel, ExclusionConeCreateModel
from app.entities.ExclusionCone import ExclusionCone


class ExclusionConeService:
    @staticmethod
    def create_exclusion_cone(db: Session, exclusion_cone: ExclusionConeCreateModel):
        ex_cone = ExclusionCone(**exclusion_cone.model_dump())
        db.add(ex_cone)
        db.commit()
        db.refresh(ex_cone)
        return ex_cone

    @staticmethod
    def update_exclusion_cone(db: Session, exclusion_cone: ExclusionConeModel):
        statement = select(ExclusionCone).where(ExclusionCone.id == exclusion_cone.id)
        existing_ex_cone = db.exec(statement).first()
        if existing_ex_cone:
            for key, value in exclusion_cone.model_dump().items():
                setattr(existing_ex_cone, key, value)
            db.commit()
            db.refresh(existing_ex_cone)
            return existing_ex_cone
        else:
            create_model = ExclusionConeCreateModel(**exclusion_cone.model_dump())
            return ExclusionConeService.create_exclusion_cone(db, create_model)

    @staticmethod
    def get_exclusion_cones(db: Session):
        statement = select(ExclusionCone)
        return db.exec(statement).all()

    @staticmethod
    def get_exclusion_cone(db: Session, ex_cone_id: uuid.UUID):
        statement = select(ExclusionCone).where(ExclusionCone.id == ex_cone_id)
        return db.exec(statement).first()

    @staticmethod
    def delete_exclusion_cone(db: Session, ex_cone_id: uuid.UUID):
        statement = select(ExclusionCone).where(ExclusionCone.id == ex_cone_id)
        exclusion_cone = db.exec(statement).first()
        if exclusion_cone:
            db.delete(exclusion_cone)
            db.commit()
            # if need be, we can return the deleted object; for now it's just a success status
            return True
        return False
