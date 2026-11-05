from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.db.models import Todo, ChecklistItem
from backend.app.schemas.calendar_todo import TodoResponse, ChecklistResponse


class TodoCreate(BaseModel):
    user_id: str
    title: str


class TodoToggle(BaseModel):
    is_completed: bool

router = APIRouter()


# ---------------- Todos ----------------

@router.get("/todos", response_model=List[TodoResponse], tags=["Todos"])
def get_todos(
    user_id: Optional[str] = Query(None, description="사용자 ID로 필터링 (내 할일만 조회)"),
    db: Session = Depends(get_db)
):
    query = db.query(Todo)
    if user_id:
        query = query.filter(Todo.user_id == user_id)
    todos = query.order_by(Todo.created_at.desc()).all()
    return [
        TodoResponse(id=t.todo_id, user_id=t.user_id, title=t.title, done=t.is_completed)
        for t in todos
    ]


@router.post("/todos", response_model=TodoResponse, status_code=201, tags=["Todos"])
def create_todo(
    todo_in: TodoCreate,
    db: Session = Depends(get_db)
):
    new_todo = Todo(user_id=todo_in.user_id, title=todo_in.title, is_completed=False)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return TodoResponse(id=new_todo.todo_id, user_id=new_todo.user_id, title=new_todo.title, done=new_todo.is_completed)


@router.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
def update_todo(
    todo_id: str,
    todo_in: TodoToggle,
    db: Session = Depends(get_db)
):
    todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.is_completed = todo_in.is_completed
    todo.completed_at = datetime.utcnow() if todo_in.is_completed else None
    db.commit()
    db.refresh(todo)
    return TodoResponse(id=todo.todo_id, user_id=todo.user_id, title=todo.title, done=todo.is_completed)


@router.delete("/todos/{todo_id}", tags=["Todos"])
def delete_todo(todo_id: str, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"success": True, "message": "Todo deleted"}


# ---------------- Checklist ----------------

@router.get("/checklist", response_model=List[ChecklistResponse], tags=["Checklist"])
def get_checklist(db: Session = Depends(get_db)):
    items = db.query(ChecklistItem).order_by(ChecklistItem.sort_order.asc()).all()
    return [
        ChecklistResponse(id=item.item_id, category=item.category, name=item.item_name, checked=item.is_checked, sort_order=item.sort_order)
        for item in items
    ]


@router.patch("/checklist/{item_id}/toggle", tags=["Checklist"])
def toggle_checklist_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(ChecklistItem).filter(ChecklistItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    item.is_checked = not item.is_checked
    db.commit()
    return {"id": item.item_id, "checked": item.is_checked}


@router.post("/checklist/check-all", tags=["Checklist"])
def check_all_items(db: Session = Depends(get_db)):
    db.query(ChecklistItem).update({"is_checked": True})
    db.commit()
    return {"success": True, "message": "All checklist items marked as checked"}
