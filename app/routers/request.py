from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

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
def bookings():
    try:
        future_reqs = [
            map_to_response_model(booking) for booking in get_db_contact_times()
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
def rf_time(request: RFTimeRequestModel):
    schedule_rf(request)
    return request


@router.post(
    "/contact",
    summary="Ground Station Contact Request",
    response_model=ContactRequestModel,
    response_description="Simple success string for now",
)
def contact(request: ContactRequestModel):
    schedule_contact(request)
    return request
