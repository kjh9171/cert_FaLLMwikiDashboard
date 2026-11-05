from typing import Optional
from datetime import date
from pydantic import BaseModel


class UserCreate(BaseModel):
    user_id: str
    name: str
    role: str = "MEMBER"  # ADMIN, MEMBER, CHILD
    color_code: str = "#4299E1"
    avatar_initial: str = "?"
    birth_date: Optional[date] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    color_code: Optional[str] = None
    avatar_initial: Optional[str] = None
    birth_date: Optional[date] = None


class UserResponse(BaseModel):
    user_id: str
    name: str
    role: str
    color_code: str
    avatar_initial: str
    birth_date: Optional[date] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
