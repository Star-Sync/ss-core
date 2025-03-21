from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from ..services import auth
from ..models.auth import User, UserCreate, UserRead
from app.services.db import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


@router.post("/token", response_model=auth.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserRead)
async def register_user_endpoint(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Call the service function instead of handling DB logic here
        new_user = auth.register_user(db, user_data)
    except ValueError as e:
        # Handle specific validation errors from the service
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the specific error
        print(f"Registration error: {str(e)}")
        # Rollback the transaction - this is now handled in the service
        db.rollback()
        # Re-raise as HTTP exception
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    return new_user


@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(auth.get_current_active_user)):
    return current_user
