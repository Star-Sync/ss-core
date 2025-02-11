import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.exclusion_cone import ExclusionConeModel, ExclusionConeCreateModel
from sqlmodel import Session
from app.services.db import get_db
from app.services.exclusion_cone import ExclusionConeService

router = APIRouter(
    prefix="/excones",
    tags=["Exclusion Cone"],
    responses={404: {"description": "Exclusion cone not found"}},
)


# POST /api/v1/excones
@router.post(
    "/",
    summary="Create a new ExclusionCone",
    response_model=ExclusionConeModel,
    response_description="ExclusionCone created response",
)
def create_exclusion_cone(
    request: ExclusionConeCreateModel, db: Session = Depends(get_db)
):
    new_exclusion_cone = ExclusionConeService.create_exclusion_cone(db, request)
    return ExclusionConeModel(**new_exclusion_cone.model_dump())


# PUT /api/v1/excones/
@router.put(
    "/",
    summary="Update a exclusion_cone",
    response_model=ExclusionConeModel,
    response_description="ExclusionCone updated response",
)
def update_exclusion_cone(request: ExclusionConeModel, db: Session = Depends(get_db)):
    exclusion_cone = ExclusionConeService.update_exclusion_cone(db, request)
    return ExclusionConeModel(**exclusion_cone.model_dump())


# GET /api/v1/excones
@router.get(
    "/",
    summary="Get a list of all exclusion_cones",
    response_model=List[ExclusionConeModel],
)
def get_exclusion_cones(db: Session = Depends(get_db)):
    exclusion_cones = ExclusionConeService.get_exclusion_cones(db)
    return [
        ExclusionConeModel(**exclusion_cone.model_dump())
        for exclusion_cone in exclusion_cones
    ]


# GET /api/v1/excones/{excone_id}
@router.get(
    "/{exclusion_cone_id}",
    summary="Get a exclusion_cone by id",
    response_model=ExclusionConeModel,
)
def get_exclusion_cone(exclusion_cone_id: uuid.UUID, db: Session = Depends(get_db)):
    exclusion_cone = ExclusionConeService.get_exclusion_cone(db, exclusion_cone_id)
    if exclusion_cone is None:
        raise HTTPException(
            status_code=404, detail=router.responses[404]["description"]
        )
    return ExclusionConeModel(**exclusion_cone.model_dump())


# DELETE /api/v1/exclusion_cone/{exclusion_cone_id}
@router.delete("/{exclusion_cone_id}", summary="Delete a exclusion_cone")
def delete_exclusion_cone(exclusion_cone_id: uuid.UUID, db: Session = Depends(get_db)):
    if not ExclusionConeService.delete_exclusion_cone(db, exclusion_cone_id):
        raise HTTPException(
            status_code=404, detail=router.responses[404]["description"]
        )
    return {"detail": "ExclusionCone deleted successfully"}
