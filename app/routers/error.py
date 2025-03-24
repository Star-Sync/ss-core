from typing import Dict, Any
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


def getErrorResponses(code: int) -> Dict[int, Dict[str, Any]]:
    if code == 404:
        return {
            404: {
                "description": "Resource not found",
                "model": ErrorResponse,
                "content": _getErrorContentExample(),
            }
        }
    elif code == 409:
        return {
            409: {
                "description": "Conflict with existing resource",
                "model": ErrorResponse,
                "content": _getErrorContentExample(),
            }
        }
    elif code == 503:
        return {
            503: {
                "description": "Database unavailable or error occurred",
                "model": ErrorResponse,
                "content": _getErrorContentExample(),
            }
        }
    else:
        return {
            500: {
                "description": "Unexpected server error",
                "model": ErrorResponse,
                "content": _getErrorContentExample(),
            }
        }


def _getErrorContentExample() -> Dict[str, Any]:
    return {"application/json": {"example": {"detail": "Error details"}}}
