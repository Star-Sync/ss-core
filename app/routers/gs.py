from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..models.gs import MockRequest
from ..services.gs import generate_mock_data
from typing import List

router = APIRouter(
    prefix="/gs",
    tags=["gs"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/mock",
    summary="Generate mock data for ground stations",
    response_model=List[bool],
    response_description="List of boolean values that are equal to the ground stations availability at each time interval",
)
async def gs_mock(request: MockRequest):
    return JSONResponse(content=generate_mock_data(request))
