import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.models.satellite import SatelliteModel, SatelliteCreateModel
from sqlmodel import Session
from app.services.db import get_db
from app.services.satellite import SatelliteService

router = APIRouter(
    prefix="/satellite",
    tags=["Satellite"],
    responses={404: {"description": "Satellite not found"}},
)


# POST /api/v1/satellite
@router.post(
    "/",
    summary="Create a new Satellite",
    response_model=SatelliteModel,
    response_description="Satellite created response",
)
def create_satellite(request: SatelliteCreateModel, db: Session = Depends(get_db)):
    new_satellite = SatelliteService.create_satellite(db, request)
    return SatelliteModel(**new_satellite.model_dump())


# PUT /api/v1/satellite/
@router.put(
    "/",
    summary="Update a Satellite",
    response_model=SatelliteModel,
    response_description="Satellite updated response",
)
def update_satellite(request: SatelliteModel, db: Session = Depends(get_db)):
    satellite = SatelliteService.update_satellite(db, request)
    return SatelliteModel(**satellite.model_dump())


# GET /api/v1/satellite
@router.get(
    "/",
    summary="Get a list of all satellites",
    response_model=List[SatelliteModel],
)
def get_satellites(db: Session = Depends(get_db)):
    satellites = SatelliteService.get_satellites(db)
    return [SatelliteModel(**satellite.model_dump()) for satellite in satellites]


# GET /api/v1/satellite/{satellite_id}
@router.get(
    "/{satellite_id}",
    summary="Get a satellite by id",
    response_model=SatelliteModel,
)
def get_satellite(satellite_id: uuid.UUID, db: Session = Depends(get_db)):
    satellite = SatelliteService.get_satellite(db, satellite_id)
    if satellite is None:
        raise HTTPException(
            status_code=404, detail=router.responses[404]["description"]
        )
    return SatelliteModel(**satellite.model_dump())


# DELETE /api/v1/satellite/{satellite_id}
@router.delete("/{satellite_id}", summary="Delete a Satellite")
def delete_satellite(satellite_id: uuid.UUID, db: Session = Depends(get_db)):
    if not SatelliteService.delete_satellite(db, satellite_id):
        raise HTTPException(
            status_code=404, detail=router.responses[404]["description"]
        )
    return {"detail": "Satellite deleted successfully"}
