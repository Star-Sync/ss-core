from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..models.request import RFTimeRequestModel, ContactRequestModel

router = APIRouter(
    prefix="/request",
    tags=["request"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/rf-time",
    summary="Ground Station RF Time Request ",
    response_model=str,
    response_description="Simple success string for now",
)
async def gs_mock(request: RFTimeRequestModel):
    return JSONResponse(content="RF Time Success!")


@router.post(
    "/contact",
    summary="Ground Station Contact Request",
    response_model=str,
    response_description="Simple success string for now",
)
async def gs_mock(request: ContactRequestModel):
    return JSONResponse(content="Contact Success!")
