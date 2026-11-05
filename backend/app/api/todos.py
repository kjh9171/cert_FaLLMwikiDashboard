from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.app.db.session import get_db
from backend.app.db.models import Todo, ChecklistItem
from backend.app.schemas.calendar_todo import TodoResponse, ChecklistResponse

router = APIRouter()

# Todos
@router.get("/todos", response_model=List[TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return [
        TodoResponse(
            id=t.todo_id,
            user_id=t.user_id,
            title=t.title,
            done=t.is_completed
        )
        for t in todos
    ]

@router.patch("/todos/{todo_id}/toggle")
def toggle_todo(todo_id: str, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.is_completed = not todo.is_completed
    todo.completed_at = datetime.utcnow() if todo.is_completed else None
    db.commit()
    return {"id": todo.todo_id, "done": todo.is_completed}

# Checklist
@router.get("/checklist", response_model=List[ChecklistResponse])
def get_checklist(db: Session = Depends(get_db)):
    items = db.query(ChecklistItem).order_by(ChecklistItem.sort_order.asc()).all()
    return [
        ChecklistResponse(
            id=item.item_id,
            category=item.category,
            name=item.item_name,
            checked=item.is_checked,
            sort_order=item.sort_order
        )
        for item in items
    ]

@router.patch("/checklist/{item_id}/toggle")
def toggle_checklist_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(ChecklistItem).filter(ChecklistItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    item.is_checked = not item.is_checked
    db.commit()
    return {"id": item.item_id, "checked": item.is_checked}

@router.post("/checklist/check-all")
def check_all_items(db: Session = Depends(get_db)):
    db.query(ChecklistItem).update({"is_checked": True})
    db.commit()
    return {"success": True, "message": "All checklist items marked as checked"}

