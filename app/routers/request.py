from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from ..models.request import RFTimeRequestModel, ContactRequestModel
from ..services.request import get_db_contact_times, schedule_contact, schedule_rf


router = APIRouter(
    prefix="/request",
    tags=["request"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    summary="Get all the scheduled requests",
    response_model=List[str],
    response_description="Scheduled requests",
)
def rf_time():
    # need to figure out the serialization; want to use GeneralContactResponseModel for that
    # for now, the response of bookings is List[str]
    future_reqs = [repr(booking) for booking in get_db_contact_times()]
    print(future_reqs)
    return JSONResponse(content=future_reqs)

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
