from fastapi import HTTPException
# from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, Session
from app.models.user import UserModel, UserCreateModel, UserUpdateModel
from app.entities.User import User

class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreateModel):
        new_user = User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, request: UserUpdateModel, current_user: UserModel):
        statement = select(User).where(User.id == user_id)
        existing_user = db.exec(statement).first()

        if not existing_user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_user, key, value)

        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    @staticmethod
    def get_users(db: Session):
        statement = select(User)
        return db.exec(statement).all()
    
    @staticmethod
    def get_user(db: Session, user_id: int, current_user:UserModel):
        statement = select(User).where(User.id == user_id)
        user = db.exec(statement).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int, current_user: UserModel):
        statement = select(User).where(User.id == user_id)
        user = db.exec(statement).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        db.delete(user)
        db.commit()
        return {"detail": "User {user_id} deleted successfully"}
