from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, Session
from app.models.user import UserModel, UserCreateModel, UserUpdateModel
from app.entities.User import User