from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from ..auth import jwt
from ..auth.models import User, UserCreate, UserRead
from app.services.db import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
    )

@router.post("/token", response_model=jwt.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = jwt.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=jwt.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserRead)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    
    try: 
        # Check if username already exists
        stmt = select(User).where(User.username == user_data.username)
        existing_user = db.exec(stmt).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Check if email already exists
        stmt = select(User).where(User.email == user_data.email)
        existing_email = db.exec(stmt).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = jwt.get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    
    except Exception as e:
         # Log the specific error
        print(f"Registration error: {str(e)}")
        # Rollback the transaction
        db.rollback()
        # Re-raise as HTTP exception
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    return new_user

@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(jwt.get_current_active_user)):
    return current_user
