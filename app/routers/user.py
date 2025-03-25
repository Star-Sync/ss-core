from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlmodel import Session
from app.models.user import UserModel, UserUpdateModel
from app.routers.error import getErrorResponses
from app.services.db import get_db
from app.services.user import UserService
from app.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["User Management"])


# PATCH /api/v1/users/{user_id}
@router.patch(
    "/{user_id}",
    summary="Update user",
    response_model=UserModel,
    response_description="User {user_id} successully updated",
    responses={**getErrorResponses(403), **getErrorResponses(404), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def update_user(
    user_id: int,
    request: UserUpdateModel,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return UserService.update_user(db, user_id, request, current_user)


# GET /api/v1/users
@router.get(
    "/",
    summary="Get a list of all users",
    response_model=List[UserModel],
    response_description="List of user objects",
    responses={**getErrorResponses(403), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def get_users(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    return UserService.get_users(db, current_user)


# GET /api/v1/users/{user_id}
@router.get(
    "/{user_id}",
    summary="Get a user from their ID",
    response_model=UserModel,
    responses={**getErrorResponses(403), **getErrorResponses(404), **getErrorResponses(503), **getErrorResponses(500)},  # type: ignore[dict-item]
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return UserService.get_user(db, user_id, current_user)
