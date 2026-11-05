from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.db.session import get_db
from backend.app.db.models import CalendarEvent
from backend.app.schemas.calendar_todo import CalendarEventCreate, CalendarEventResponse

router = APIRouter()


@router.get("/events", response_model=List[CalendarEventResponse], tags=["Calendar"])
def get_calendar_events(
    user_id: Optional[str] = Query(None, description="사용자 ID로 필터링 (내 일정 조회)"),
    db: Session = Depends(get_db)
):
    """일정 목록 조회 (user_id 지정 시 해당 사용자의 일정만 조회)"""
    query = db.query(CalendarEvent).order_by(CalendarEvent.start_time.asc())
    if user_id:
        query = query.filter(CalendarEvent.user_id == user_id)
    events = query.all()
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


@router.get("/events/{event_id}", response_model=CalendarEventResponse, tags=["Calendar"])
def get_calendar_event(event_id: str, db: Session = Depends(get_db)):
    """특정 일정 조회"""
    event = db.query(CalendarEvent).filter(CalendarEvent.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return CalendarEventResponse(
        event_id=event.event_id,
        title=event.title,
        start_time=event.start_time.isoformat(),
        end_time=event.end_time.isoformat(),
        is_all_day=event.is_all_day,
        category=event.category,
        color_tag=event.color_tag,
        description=event.description
    )


@router.post("/events", response_model=CalendarEventResponse, status_code=201, tags=["Calendar"])
def create_calendar_event(
    ev_in: CalendarEventCreate,
    db: Session = Depends(get_db)
):
    """내 일정 등록 (user_id 지정 필수)"""
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


@router.put("/events/{event_id}", response_model=CalendarEventResponse, tags=["Calendar"])
def update_calendar_event(
    event_id: str,
    ev_in: CalendarEventCreate,
    db: Session = Depends(get_db)
):
    """일정 수정 (내 일정 수정)"""
    event = db.query(CalendarEvent).filter(CalendarEvent.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.user_id = ev_in.user_id
    event.title = ev_in.title
    event.start_time = ev_in.start_time
    event.end_time = ev_in.end_time
    event.is_all_day = ev_in.is_all_day
    event.category = ev_in.category
    event.color_tag = ev_in.color_tag
    event.description = ev_in.description

    db.commit()
    db.refresh(event)

    return CalendarEventResponse(
        event_id=event.event_id,
        title=event.title,
        start_time=event.start_time.isoformat(),
        end_time=event.end_time.isoformat(),
        is_all_day=event.is_all_day,
        category=event.category,
        color_tag=event.color_tag,
        description=event.description
    )


@router.delete("/events/{event_id}", tags=["Calendar"])
def delete_calendar_event(event_id: str, db: Session = Depends(get_db)):
    """일정 삭제 (내 일정 삭제)"""
    event = db.query(CalendarEvent).filter(CalendarEvent.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()
    return {"success": True, "message": f"Event {event_id} deleted"}
