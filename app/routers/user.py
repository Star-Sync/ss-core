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
def create_user(
    request: UserCreateModel,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Must be an admin")
    return UserService.create_user(db, request)

# PATCH /api/v1/user/{user_id}
@router.patch(
    "/{user_id}",
    summary="Update user",
    response_model=UserModel,
    response_description="User {user_id} successully updated",
)
def update_user(
    user_id: int,
    request: UserUpdateModel,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return UserService.update_user(db, user_id, request, current_user)

# GET /api/v1/user
@router.get(
    "/",
    summary="Get a list of all users",
    response_model=List[UserModel],
)
def get_users(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    return UserService.get_users(db)

# GET /api/v1/user/{user_id}
@router.get(
    "/{user_id}",
    summary="Get a user from their ID",
    response_model=UserModel,
)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return UserService.get_user(db, user_id, current_user)