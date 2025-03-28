from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, Session
from app.models.user import UserModel, UserUpdateModel
from app.entities.User import User
from app.services.auth import get_password_hash


class UserService:
    @staticmethod
    def update_user(
        db: Session, user_id: int, request: UserUpdateModel, current_user: UserModel
    ) -> User:
        try:
            existing_user = UserService.get_user(
                db, user_id, current_user
            )  # already checks for admin rights, no need to check again

            update_data = request.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key == "password":
                    setattr(existing_user, "hashed_password", get_password_hash(value))
                else:
                    setattr(existing_user, key, value)

            db.commit()
            db.refresh(existing_user)
            return existing_user

        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Database error while updating user {user_id}: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while updating satellite {user_id}: {str(e)}",
            )

    @staticmethod
    def get_users(db: Session, current_user: UserModel) -> list[User]:
        try:
            if current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Permission denied")

            statement = select(User)
            users = db.exec(statement).all()

            return list(users)

        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Database error while fetching users: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while fetching users: {str(e)}",
            )

    @staticmethod
    def get_user(db: Session, user_id: int, current_user: UserModel) -> User:
        try:
            if current_user.role != "admin" and current_user.id != user_id:
                raise HTTPException(status_code=403, detail="Permission denied")

            statement = select(User).where(User.id == user_id)
            user = db.exec(statement).first()

            if not user:
                raise HTTPException(
                    status_code=404, detail=f"User with ID {user_id} not found"
                )
            return user

        except HTTPException as http_e:
            raise http_e
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Database error while fetching user {user_id}: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while fetching user {user_id}: {str(e)}",
            )
