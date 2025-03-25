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
from app.entities.Request import (
    ContactRequest,
    RFRequest,
)
from app.services.request import RequestService, Contact
import logging
from app.routers.error import getErrorResponses

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/request",
    tags=["Request"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    summary="Get all requests",
    response_model=List[GeneralContactResponseModel],
    responses={**getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def get_requests(
    db: Session = Depends(get_db),
):
    try:
        return RequestService.get_all_transformed_requests(db)
    except Exception as e:
        logger.error(f"Error getting all requests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/bookings",
    summary="Get all bookings",
    response_model=List[Contact],
    responses={**getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def get_bookings(
    db: Session = Depends(get_db),
):
    try:
        return RequestService.get_bookings(db)
    except Exception as e:
        logger.error(f"Error getting bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sample",
    summary="runs a sample demo of the service",
    response_model=List[GeneralContactResponseModel],
    responses={**getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def sample(
    db: Session = Depends(get_db),
):
    try:
        future_reqs = RequestService.sample(db)
        return future_reqs
    except ValueError as e:
        logger.error(f"Validation error in sample: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in sample: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/rf-time",
    summary="Ground Station RF Time Request",
    response_model=RFTimeRequestModel,
    response_description="Request body",
    responses={**getErrorResponses(400), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def rf_time(request: RFTimeRequestModel, db: Session = Depends(get_db)):
    try:
        created_request = RequestService.create_rf_request(db, request)
        if created_request is None:
            raise HTTPException(status_code=400, detail="Failed to create RF request")
        return request
    except ValueError as e:
        logger.error(f"Validation error creating RF request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating RF request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/contact",
    summary="Ground Station Contact Request",
    response_model=ContactRequest,
    response_description="Simple success string for now",
    responses={**getErrorResponses(400), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def contact(request: ContactRequestModel, db: Session = Depends(get_db)):
    try:
        resp = RequestService.create_contact_request(db, request)
        if resp is None:
            raise HTTPException(
                status_code=400, detail="Failed to create contact request"
            )
        return resp
    except ValueError as e:
        logger.error(f"Validation error creating contact request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating contact request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/rf-time/{request_id}",
    summary="Get RF Time Request by ID",
    response_model=RFRequest,
    responses={**getErrorResponses(404), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def get_rf_time_request(request_id: UUID, db: Session = Depends(get_db)):
    try:
        request = RequestService.get_rf_time_request(db, request_id)
        if request is None:
            raise HTTPException(
                status_code=404,
                detail=f"RF Time Request with ID {request_id} not found",
            )
        return request
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting RF time request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/rf-time/{request_id}",
    summary="Delete RF Time Request by ID",
    responses={**getErrorResponses(404), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def delete_rf_time_request(request_id: UUID, db: Session = Depends(get_db)):
    try:
        request = RequestService.get_rf_time_request(db, request_id)
        if request is None:
            raise HTTPException(
                status_code=404,
                detail=f"RF Time Request with ID {request_id} not found",
            )
        RequestService.delete_rf_time_request(db, request_id)
        return {"message": "RF Time Request deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting RF time request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/contact/{request_id}",
    summary="Get Contact Request by ID",
    response_model=ContactRequestModel,
    responses={**getErrorResponses(404), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def get_contact_request(request_id: UUID, db: Session = Depends(get_db)):
    try:
        request = RequestService.get_contact_request(db, request_id)
        if request is None:
            raise HTTPException(
                status_code=404,
                detail=f"Contact Request with ID {request_id} not found",
            )
        return request
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contact request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/contact/{request_id}",
    summary="Delete Contact Request by ID",
    responses={**getErrorResponses(404), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def delete_contact_request(request_id: UUID, db: Session = Depends(get_db)):
    try:
        request = RequestService.get_contact_request(db, request_id)
        if request is None:
            raise HTTPException(
                status_code=404,
                detail=f"Contact Request with ID {request_id} not found",
            )
        RequestService.delete_contact_request(db, request_id)
        return {"message": "Contact Request deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contact request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
