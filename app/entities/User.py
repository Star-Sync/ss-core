from datetime import datetime
from typing import List, Optional
from sqlmodel import ARRAY, JSON, Column, SQLModel, Field, String  # type: ignore


class User(SQLModel, table=True):
    """User model for authentication"""

    __tablename__: str = "users"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    first_name: Optional[str] = Field(nullable=False, default="")
    last_name: Optional[str] = Field(nullable=False, default="")
    role: str = Field(nullable=False, default="MISSION_USER")
    mission_access: Optional[List[str]] = Field(
        default_factory=list, sa_column=Column(ARRAY(String))
    )


class UserCreate(SQLModel):
    """Schema for user creation"""

    username: str
    email: str
    password: str
