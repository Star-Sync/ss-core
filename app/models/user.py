from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class UserBaseModel(BaseModel):
    username: str = Field(description="Username", examples=["johndoe"])
    email: str = Field(description="User email", examples=["johndoe@email.com"])
    is_active: bool = Field(description="Is user active", examples=[True])
    first_name: Optional[str] = Field(
        description="User's first name", examples=["John"]
    )
    last_name: Optional[str] = Field(description="User's last name", examples=["Doe"])
    role: str = Field(
        description="User's role (admin or user)", examples=["admin", "user"]
    )


class UserModel(UserBaseModel):
    """
    Pydantic model to represent a user.
    """

    id: int = Field(description="User ID", examples=[1])
    created_at: Optional[datetime] = Field(
        description="Date user was created", examples=[datetime.now()]
    )

    class Config:
        from_attributes = True


class UserUpdateModel(BaseModel):
    """
    Pydantic model for updating user details.
    """

    username: Optional[str] = Field(
        default=None, description="Username", examples=["johndoe"]
    )
    password: Optional[str] = Field(
        default=None, description="Password", examples=["password"]
    )
    email: Optional[str] = Field(
        default=None, description="User email", examples=["johndoe@gmail.com"]
    )
    is_active: Optional[bool] = Field(
        default=None, description="Is user active", examples=[True]
    )
    first_name: Optional[str] = Field(
        default=None, description="User's first name", examples=["John"]
    )
    last_name: Optional[str] = Field(
        default=None, description="User's last name", examples=["Doe"]
    )
    role: Optional[str] = Field(
        default=None,
        description="User's role (admin or user)",
        examples=["admin", "user"],
    )

    @field_validator("role")
    def validate_role(cls, value):
        if value not in {"admin", "user"}:
            raise ValueError("Role must be either 'admin' or 'user'")
        return value

    class Config:
        from_attributes = True
