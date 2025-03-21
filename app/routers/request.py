from typing import List
from fastapi import APIRouter, HTTPException, Depends
from app.services.db import get_db
from sqlmodel import Session
from uuid import UUID
from app.models.request import (
    GeneralContactResponseModel,
    RFTimeRequestModel,
    ContactRequestModel,
)
from ..services.request import RequestService

router = APIRouter(
    prefix="/request",
    tags=["Request"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    summary="Get all requests",
    response_model=List[GeneralContactResponseModel],
)
def get_requests(
    db: Session = Depends(get_db),
):
    return RequestService.get_all_requests(db)


@router.get(
    "/sample",
    summary="runs a sample demo of the service",
    response_model=List[GeneralContactResponseModel],
)
def sample(
    db: Session = Depends(get_db),
):
    try:
        future_reqs = RequestService.sample(db)

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
    RequestService.create_rf_request(db, request)
    return request


@router.post(
    "/contact",
    summary="Ground Station Contact Request",
    response_model=ContactRequestModel,
    response_description="Simple success string for now",
)
def contact(request: ContactRequestModel, db: Session = Depends(get_db)):
    RequestService.create_contact_request(db, request)
    return request


@router.get(
    "/rf-time/{request_id}",
    summary="Get RF Time Request by ID",
    response_model=RFTimeRequestModel,
)
def get_rf_time_request(request_id: UUID, db: Session = Depends(get_db)):
    request = RequestService.get_rf_time_request(db, request_id)
    if request is None:
        raise HTTPException(
            status_code=404, detail=f"RF Time Request with ID {request_id} not found"
        )
    # Convert entity to model
    return RFTimeRequestModel(
        missionName=request.mission,
        satelliteId=request.satellite_id,
        startTime=request.start_time,
        endTime=request.end_time,
        uplinkTime=float(request.uplink_time_requested),
        downlinkTime=float(request.downlink_time_requested),
        scienceTime=float(request.science_time_requested),
        minimumNumberOfPasses=request.min_passes,
    )


@router.delete(
    "/rf-time/{request_id}",
    summary="Delete RF Time Request by ID",
)
def delete_rf_time_request(request_id: UUID, db: Session = Depends(get_db)):
    request = RequestService.get_rf_time_request(db, request_id)
    if request is None:
        raise HTTPException(
            status_code=404, detail=f"RF Time Request with ID {request_id} not found"
        )
    RequestService.delete_rf_time_request(db, request_id)
    return {"message": "RF Time Request deleted successfully"}


@router.get(
    "/contact/{request_id}",
    summary="Get Contact Request by ID",
    response_model=ContactRequestModel,
)
def get_contact_request(request_id: UUID, db: Session = Depends(get_db)):
    request = RequestService.get_contact_request(db, request_id)
    if request is None:
        raise HTTPException(
            status_code=404, detail=f"Contact Request with ID {request_id} not found"
        )
    # Convert entity to model
    return ContactRequestModel(
        missionName=request.mission,
        satelliteId=request.satellite_id,
        location="N/A",  # This field might need to be populated from ground station info
        orbit=f"SCISAT-{request.orbit}",
        uplink=request.uplink,
        telemetry=request.telemetry,
        science=request.science,
        aosTime=request.aos or request.start_time,
        rfOnTime=request.rf_on or request.start_time,
        rfOffTime=request.rf_off or request.end_time,
        losTime=request.los or request.end_time,
    )


@router.delete(
    "/contact/{request_id}",
    summary="Delete Contact Request by ID",
)
def delete_contact_request(request_id: UUID, db: Session = Depends(get_db)):
    request = RequestService.get_contact_request(db, request_id)
    if request is None:
        raise HTTPException(
            status_code=404, detail=f"Contact Request with ID {request_id} not found"
        )
    RequestService.delete_contact_request(db, request_id)
    return {"message": "Contact Request deleted successfully"}
