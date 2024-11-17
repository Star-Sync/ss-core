from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.entities.GeneralContact import GeneralContact
from app.entities.RFTime import RFTime
from ..models.request import GeneralContactResponseModel, RFTimeRequestModel, ContactRequestModel
from ..services.request import schedule


router = APIRouter(
    prefix="/request",
    tags=["request"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/rf-time",
    summary="Ground Station RF Time Request ",
    response_model=List[str],
    response_description="Scheduled requests",
)
async def rf_time(request: RFTimeRequestModel):
    bookings = await schedule(request)
    
    # need to figure out the serialization; want to use GeneralContactResponseModel for that
    # for now, the response of bookings is List[str]
    return JSONResponse(content=bookings)


@router.post(
    "/contact",
    summary="Ground Station Contact Request",
    response_model=str,
    response_description="Simple success string for now",
)
async def contact(request: ContactRequestModel):
    return JSONResponse(content="Contact Success!")
