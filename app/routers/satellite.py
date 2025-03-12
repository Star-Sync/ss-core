import uuid
from fastapi import APIRouter, Depends
from typing import List
from app.models.satellite import (
    SatelliteModel,
    SatelliteCreateModel,
    SatelliteUpdateModel,
)
from sqlmodel import Session
from app.routers.error import getErrorResponses
from app.services.db import get_db
from app.services.satellite import SatelliteService

router = APIRouter(prefix="/satellites", tags=["Satellite"])


# POST /api/v1/satellites
@router.post(
    "/",
    summary="Create a new Satellite",
    response_model=SatelliteModel,
    responses={**getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def create_satellite(request: SatelliteCreateModel, db: Session = Depends(get_db)):
    return SatelliteService.create_satellite(db, request)


# PATCH /api/v1/satellites/{satellite_id}
@router.patch(
    "/{satellite_id}",
    summary="Update a Satellite",
    response_model=SatelliteModel,
    response_description="Satellite updated response",
    responses={**getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def update_satellite(
    satellite_id: uuid.UUID,
    request: SatelliteUpdateModel,
    db: Session = Depends(get_db),
):
    return SatelliteService.update_satellite(db, satellite_id, request)


# GET /api/v1/satellites
@router.get(
    "/",
    summary="Get a list of all satellites",
    response_model=List[SatelliteModel],
    responses={**getErrorResponses(404), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def get_satellites(db: Session = Depends(get_db)):
    return SatelliteService.get_satellites(db)


# GET /api/v1/satellites/{satellite_id}
@router.get(
    "/{satellite_id}",
    summary="Get a satellite by id",
    response_model=SatelliteModel,
    responses={**getErrorResponses(404), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def get_satellite(satellite_id: uuid.UUID, db: Session = Depends(get_db)):
    return SatelliteService.get_satellite(db, satellite_id)


# DELETE /api/v1/satellites/{satellite_id}
@router.delete(
    "/{satellite_id}",
    summary="Delete a Satellite",
    response_model=SatelliteModel,
    response_description="Deleted satellite object",
    responses={**getErrorResponses(404), **getErrorResponses(409), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def delete_satellite(satellite_id: uuid.UUID, db: Session = Depends(get_db)):
    return SatelliteService.delete_satellite(db, satellite_id)
