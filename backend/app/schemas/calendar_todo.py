from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class CalendarEventCreate(BaseModel):
    user_id: Optional[str] = None
    title: str
    start_time: datetime
    end_time: datetime
    is_all_day: bool = False
    category: str
    color_tag: str
    description: Optional[str] = None

class CalendarEventResponse(BaseModel):
    event_id: str
    title: str
    start_time: str
    end_time: str
    is_all_day: bool
    category: str
    color_tag: str
    description: Optional[str] = None

class TodoResponse(BaseModel):
    id: str
    user_id: str
    title: str
    done: bool

class ChecklistResponse(BaseModel):
    id: str
    category: str
    name: str
    checked: bool
    sort_order: int

