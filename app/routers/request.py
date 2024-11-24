from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from ..services.db import get_db

from ..models.request import (
    GeneralContactResponseModel,
    RFTimeRequestModel,
    ContactRequestModel,
)
from ..services.request import (
    get_db_contact_times,
    schedule_contact,
    schedule_rf,
    map_to_response_model,
)


router = APIRouter(
    prefix="/request",
    tags=["request"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    summary="Get all the scheduled requests",
    response_model=List[GeneralContactResponseModel],
    response_description="Scheduled requests",
)
def bookings(db: Session = Depends(get_db)):
    try:
        future_reqs = [
            map_to_response_model(booking) for booking in get_db_contact_times(db)
        ]
        return future_reqs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/rf-time",
    summary="Ground Station RF Time Request",
    response_model=RFTimeRequestModel,
    response_description="Request body",
)
def rf_time(request: RFTimeRequestModel, db: Session = Depends(get_db)):
    schedule_rf(request, db)
    return request


@router.post(
    "/contact",
    summary="Ground Station Contact Request",
    response_model=ContactRequestModel,
    response_description="Simple success string for now",
)
def contact(request: ContactRequestModel, db: Session = Depends(get_db)):
    schedule_contact(request, db)
    return request


@router.get(
    "/initdb",
    summary="Initialize the database",
    response_description="Database and tables created",
)
def initdb(db: Session = Depends(get_db)):
    from ..services.db import create_db_and_tables
    from ..services.request import init_db_contact_times

    create_db_and_tables()
    init_db_contact_times(db)
    return {"message": "Database and tables created"}
