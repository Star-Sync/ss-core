import uuid
from fastapi import APIRouter, Depends
from typing import List
from app.models.exclusion_cone import (
    ExclusionConeModel,
    ExclusionConeCreateModel,
    ExclusionConeUpdateModel,
)
from sqlmodel import Session
from app.routers.error import getErrorResponses
from app.services.db import get_db
from app.services.exclusion_cone import ExclusionConeService

router = APIRouter(prefix="/excones", tags=["Exclusion Cone"])


# POST /api/v1/excones
@router.post(
    "/",
    summary="Create a new ExclusionCone",
    response_model=ExclusionConeModel,
    response_description="Created exclusion cone object",
    responses={**getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def create_exclusion_cone(
    request: ExclusionConeCreateModel, db: Session = Depends(get_db)
):
    return ExclusionConeService.create_exclusion_cone(db, request)


# PATCH /api/v1/excones/{excone_id}
@router.patch(
    "/{excone_id}",
    summary="Update exclusion cone",
    response_model=ExclusionConeModel,
    response_description="Updated exclusion cone object",
    responses={**getErrorResponses(404), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def update_exclusion_cone(
    excone_id: uuid.UUID,
    request: ExclusionConeUpdateModel,
    db: Session = Depends(get_db),
):
    return ExclusionConeService.update_exclusion_cone(db, excone_id, request)


# GET /api/v1/excones
@router.get(
    "/",
    summary="Get a list of all exclusion_cones",
    response_model=List[ExclusionConeModel],
    response_description="List of exclusion cone objects",
    responses={**getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def get_exclusion_cones(db: Session = Depends(get_db)):
    return ExclusionConeService.get_exclusion_cones(db)


# GET /api/v1/excones/{excone_id}
@router.get(
    "/{excone_id}",
    summary="Get a exclusion_cone by id",
    response_model=ExclusionConeModel,
    response_description="Specific exclusion object",
    responses={**getErrorResponses(404), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def get_exclusion_cone(excone_id: uuid.UUID, db: Session = Depends(get_db)):
    return ExclusionConeService.get_exclusion_cone(db, excone_id)


# DELETE /api/v1/exclusion_cone/{exclusion_cone_id}
@router.delete(
    "/{excone_id}",
    summary="Delete a exclusion_cone",
    response_model=ExclusionConeModel,
    response_description="Deleted exclusion cone object",
    responses={**getErrorResponses(404), **getErrorResponses(409), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def delete_exclusion_cone(excone_id: uuid.UUID, db: Session = Depends(get_db)):
    return ExclusionConeService.delete_exclusion_cone(db, excone_id)
