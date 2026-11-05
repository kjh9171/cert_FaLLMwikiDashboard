from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.app.db.session import get_db
from backend.app.db.models import CalendarEvent
from backend.app.schemas.calendar_todo import CalendarEventCreate, CalendarEventResponse

router = APIRouter()

@router.get("/events", response_model=List[CalendarEventResponse])
def get_calendar_events(db: Session = Depends(get_db)):
    events = db.query(CalendarEvent).order_by(CalendarEvent.start_time.asc()).all()
    return [
        CalendarEventResponse(
            event_id=e.event_id,
            title=e.title,
            start_time=e.start_time.isoformat(),
            end_time=e.end_time.isoformat(),
            is_all_day=e.is_all_day,
            category=e.category,
            color_tag=e.color_tag,
            description=e.description
        )
        for e in events
    ]

@router.post("/events", response_model=CalendarEventResponse, status_code=201)
def create_calendar_event(
    ev_in: CalendarEventCreate,
    db: Session = Depends(get_db)
):
    new_event = CalendarEvent(
        user_id=ev_in.user_id,
        title=ev_in.title,
        start_time=ev_in.start_time,
        end_time=ev_in.end_time,
        is_all_day=ev_in.is_all_day,
        category=ev_in.category,
        color_tag=ev_in.color_tag,
        description=ev_in.description
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return CalendarEventResponse(
        event_id=new_event.event_id,
        title=new_event.title,
        start_time=new_event.start_time.isoformat(),
        end_time=new_event.end_time.isoformat(),
        is_all_day=new_event.is_all_day,
        category=new_event.category,
        color_tag=new_event.color_tag,
        description=new_event.description
    )

