from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlmodel import Session
from app.models.user import UserModel, UserUpdateModel, UserCreateModel
from app.services.db import get_db
from app.services.user import UserService
from app.services.auth import get_current_user

router = APIRouter(prefix="/user", tags=["User Management"], responses={404: {"description": "User not found"}})



# POST /api/v1/user
@router.post(
    "/",
    summary="Create a new user",
    response_model=UserModel,
    response_description="User successfully created",
)
# def create_user(
#     request: UserCreateModel,
#     db: Session = Depends(get_db),
#     current_user: UserModel = Depends(get_current_user)
# ):
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Must be an admin")
#     return UserService.create_user(db, request)