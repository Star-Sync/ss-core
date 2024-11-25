from typing import List
from fastapi import APIRouter, HTTPException, Depends

from app.entities.RFTime import RFTime
from app.entities.Contact import Contact
from ..models.request import (
    GeneralContactResponseModel,
    RFTimeRequestModel,
    ContactRequestModel,
)
from ..services.request import (
    SchedulerService,
    get_scheduler_service,
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
def bookings(scheduler: SchedulerService = Depends(get_scheduler_service)):
    try:
        future_reqs = [
            map_to_response_model(booking)
            for booking in scheduler.get_db_contact_times()
        ]
        return future_reqs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/rf-time",
    summary="Ground Station RF Time Request",
    response_model=RFTime,
    response_description="Request body",
)
def rf_time(
    request: RFTimeRequestModel,
    scheduler: SchedulerService = Depends(get_scheduler_service),
):
    res = scheduler.schedule_rf(request)
    return res


@router.post(
    "/contact",
    summary="Ground Station Contact Request",
    response_model=Contact,
    response_description="Simple success string for now",
)
def contact(
    request: ContactRequestModel,
    scheduler: SchedulerService = Depends(get_scheduler_service),
):
    res = scheduler.schedule_contact(request)
    return res


@router.get(
    "/initdb",
    summary="Initialize the database",
    response_description="Database and tables created",
)
def initdb(
    scheduler: SchedulerService = Depends(get_scheduler_service),
    # db: Session = Depends(get_db),
):
    from ..services.db import create_db_and_tables

    create_db_and_tables()
    scheduler.init_db_contact_times()
    return {"message": "Database and tables created"}
