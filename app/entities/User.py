from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field  # type: ignore


class User(SQLModel, table=True):
    """User model for authentication"""

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    first_name: Optional[str] = Field(nullable=False, default="")
    last_name: Optional[str] = Field(nullable=False, default="")
    role: str = Field(nullable=False, default="user", description="Role of the user (admin/user)")


class UserCreate(SQLModel):
    """Schema for user creation"""

    username: str
    email: str
    password: str


class UserRead(SQLModel):
    """Schema for user response"""

    id: int
    username: str
    email: str
    is_active: bool
