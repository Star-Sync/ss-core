#  type: ignore
# ^ remove the type: ignore from the class definition when
#  we have the correct basic types

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.services.db import get_db
from sqlmodel import Session

from app.models.request import (
    GeneralContactResponseModel,
    RFTimeRequestModel,
    ContactRequestModel,
)

# from ..services.request import (
#     get_db_contact_times,
#     schedule_contact,
#     schedule_rf,
#     map_to_response_model,
# )

from ..services.request import RequestService

router = APIRouter(
    prefix="/request",
    tags=["Request"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    summary="runs a sample demo of the service",
    response_model=List[GeneralContactResponseModel],
)
def sample(
    db: Session = Depends(get_db),
):
    try:
        # return RequestService.sample(db)
        future_reqs = RequestService.transform_contact_to_general(
            RequestService.sample(db)
        )

        return future_reqs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.get(
#     "/",
#     summary="Get all the scheduled requests",
#     response_model=List[GeneralContactResponseModel],
#     response_description="Scheduled requests",
# )
# def bookings():
#     try:
#         future_reqs = [map_to_response_model(booking) for c in get_db_contact_times()]
#         return future_reqs
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post(
#     "/rf-time",
#     summary="Ground Station RF Time Request",
#     response_model=RFTimeRequestModel,
#     response_description="Request body",
# )
# def rf_time(request: RFTimeRequestModel):
#     schedule_rf(request)
#     return request


# @router.post(
#     "/contact",
#     summary="Ground Station Contact Request",
#     response_model=ContactRequestModel,
#     response_description="Simple success string for now",
# )
# def contact(request: ContactRequestModel):
#     schedule_contact(request)
#     return request
