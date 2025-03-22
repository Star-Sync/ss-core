from typing import Optional
from pydantic import BaseModel, Field

class UserCreateModel(BaseModel):
    """
    Pydantic model class for creating a new user.
    """
    username: str = Field(description="Username", examples=["goisaiah"])
    password: str = Field(description="Password", examples=["isaiahspassword"])
    email: str = Field(description="User email", examples=["goisaiah@gmail.com"])
    first_name: str = Field(description="User's first name", examples=["Isaiah"])
    last_name: str = Field(description="User's last name", examples=["Gocool"])
    role: str = Field(description="User's role (admin or user)", examples=["admin", "user"])

class UserModel(UserCreateModel):
    """
    Pydantic model to represent a user.
    """
    id: int = Field(description="User ID", examples=[1])

    class Config:
        from_attributes = True

class UserUpdateModel(BaseModel):
    """
    Pydantic model for updating user details.
    """
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True