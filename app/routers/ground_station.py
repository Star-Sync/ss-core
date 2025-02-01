from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.models.ground_station import GroundStationModel
from sqlalchemy.orm import Session
from app.services.ground_station import GroundStationService
from app.services.db import get_db

router = APIRouter(
    prefix="/gs",
    tags=["Ground Station"],
    responses={404: {"description": "Ground station not found"}},
)


# POST /api/v1/gs
@router.post(
    "/",
    summary="Create a new ground station",
    response_model=GroundStationModel,
    response_description="Ground station created response",
)
def create_ground_station(request: GroundStationModel, db: Session = Depends(get_db)):
    new_gs = GroundStationService.create_ground_station(db, request)
    return GroundStationModel(**new_gs.model_dump())


# GET /api/v1/gs
@router.get(
    "/",
    summary="Get a list of all ground stations",
    response_model=List[GroundStationModel],
)
def get_ground_stations(db: Session = Depends(get_db)):
    gss = GroundStationService.get_ground_stations(db)
    return [GroundStationModel(**gs.model_dump()) for gs in gss]


# GET /api/v1/gs/{gs_id}
@router.get(
    "/{gs_id}", summary="Get a ground station by id", response_model=GroundStationModel
)
def get_ground_station(gs_id: int, db: Session = Depends(get_db)):
    gs = GroundStationService.get_ground_station(db, gs_id)
    if gs is None:
        raise HTTPException(
            status_code=404, detail=router.responses[404]["description"]
        )
    return GroundStationModel(**gs.model_dump())


# DELETE /api/v1/gs/{gs_id}
@router.delete("/{gs_id}", summary="Delete a ground station")
def delete_ground_station(gs_id: int, db: Session = Depends(get_db)):
    if not GroundStationService.delete_ground_station(db, gs_id):
        raise HTTPException(
            status_code=404, detail=router.responses[404]["description"]
        )
    return {"detail": "Ground station deleted successfully"}
