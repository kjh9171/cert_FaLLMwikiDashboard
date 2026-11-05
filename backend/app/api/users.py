from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.schemas.users import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("/users", response_model=List[UserResponse], tags=["Users"])
def list_users(db: Session = Depends(get_db)):
    """가족 구성원 목록 조회"""
    users = db.query(User).order_by(User.created_at.asc()).all()
    return [
        UserResponse(
            user_id=u.user_id,
            name=u.name,
            role=u.role,
            color_code=u.color_code,
            avatar_initial=u.avatar_initial,
            birth_date=u.birth_date,
            created_at=u.created_at.isoformat() if u.created_at else None
        )
        for u in users
    ]


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: str, db: Session = Depends(get_db)):
    """특정 가족 구성원 조회"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        role=user.role,
        color_code=user.color_code,
        avatar_initial=user.avatar_initial,
        birth_date=user.birth_date,
        created_at=user.created_at.isoformat() if user.created_at else None
    )


@router.post("/users", response_model=UserResponse, status_code=201, tags=["Users"])
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """가족 구성원 신규 등록 (초기 설정)"""
    existing = db.query(User).filter(User.user_id == user_in.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        user_id=user_in.user_id,
        name=user_in.name,
        role=user_in.role,
        color_code=user_in.color_code,
        avatar_initial=user_in.avatar_initial,
        birth_date=user_in.birth_date
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        user_id=new_user.user_id,
        name=new_user.name,
        role=new_user.role,
        color_code=new_user.color_code,
        avatar_initial=new_user.avatar_initial,
        birth_date=new_user.birth_date,
        created_at=new_user.created_at.isoformat() if new_user.created_at else None
    )


@router.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(user_id: str, user_in: UserUpdate, db: Session = Depends(get_db)):
    """가족 구성원 정보 수정 (이름, 역할, 색상, 아바타, 생일 등)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.name is not None:
        user.name = user_in.name
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.color_code is not None:
        user.color_code = user_in.color_code
    if user_in.avatar_initial is not None:
        user.avatar_initial = user_in.avatar_initial
    if user_in.birth_date is not None:
        user.birth_date = user_in.birth_date

    db.commit()
    db.refresh(user)

    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        role=user.role,
        color_code=user.color_code,
        avatar_initial=user.avatar_initial,
        birth_date=user.birth_date,
        created_at=user.created_at.isoformat() if user.created_at else None
    )


@router.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """가족 구성원 삭제"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"success": True, "message": f"User {user_id} deleted"}
