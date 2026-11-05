from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from backend.app.db.session import get_db
from backend.app.db.models import FinanceTransaction, FinanceBudget, FinanceCategory
from backend.app.schemas.finance import (
    TransactionCreate, TransactionResponse, FinanceSummaryResponse
)

router = APIRouter()


@router.get("/transactions", response_model=List[TransactionResponse], tags=["Finance"])
def get_transactions(
    user_id: Optional[str] = Query(None, description="사용자 ID로 필터링 (내 가계부 조회)"),
    type: Optional[str] = Query(None, description="ALL, EXPENSE, or INCOME"),
    db: Session = Depends(get_db)
):
    """거래 내역 조회 (user_id 지정 시 해당 사용자의 거래만 조회)"""
    query = db.query(FinanceTransaction).order_by(FinanceTransaction.transaction_date.desc(), FinanceTransaction.created_at.desc())
    if user_id:
        query = query.filter(FinanceTransaction.user_id == user_id)
    if type and type != "ALL":
        query = query.filter(FinanceTransaction.transaction_type == type)

    results = query.all()
    return [
        TransactionResponse(
            id=str(tx.transaction_id),
            date=tx.transaction_date.isoformat(),
            type=tx.transaction_type,
            title=tx.title,
            category=tx.category_code,
            method=tx.payment_method,
            amount=int(tx.amount),
            memo=tx.memo
        )
        for tx in results
    ]


@router.post("/transactions", response_model=TransactionResponse, status_code=201, tags=["Finance"])
def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db)
):
    """내 가계부 거래 등록 (user_id 지정)"""
    tx_date = tx_in.transaction_date or date.today()
    new_tx = FinanceTransaction(
        user_id=tx_in.user_id,
        category_code=tx_in.category,
        transaction_type=tx_in.type,
        title=tx_in.title,
        amount=tx_in.amount,
        transaction_date=tx_date,
        payment_method=tx_in.payment_method,
        memo=tx_in.memo,
        receipt_id=tx_in.receipt_id
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    return TransactionResponse(
        id=str(new_tx.transaction_id),
        date=new_tx.transaction_date.isoformat(),
        type=new_tx.transaction_type,
        title=new_tx.title,
        category=new_tx.category_code,
        method=new_tx.payment_method,
        amount=int(new_tx.amount),
        memo=new_tx.memo
    )


@router.put("/transactions/{tx_id}", response_model=TransactionResponse, tags=["Finance"])
def update_transaction(
    tx_id: str,
    tx_in: TransactionCreate,
    db: Session = Depends(get_db)
):
    """가계부 거래 수정 (내 거래 수정)"""
    tx = db.query(FinanceTransaction).filter(FinanceTransaction.transaction_id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.user_id = tx_in.user_id
    tx.category_code = tx_in.category
    tx.transaction_type = tx_in.type
    tx.title = tx_in.title
    tx.amount = tx_in.amount
    tx.transaction_date = tx_in.transaction_date or date.today()
    tx.payment_method = tx_in.payment_method
    tx.memo = tx_in.memo
    tx.receipt_id = tx_in.receipt_id

    db.commit()
    db.refresh(tx)

    return TransactionResponse(
        id=str(tx.transaction_id),
        date=tx.transaction_date.isoformat(),
        type=tx.transaction_type,
        title=tx.title,
        category=tx.category_code,
        method=tx.payment_method,
        amount=int(tx.amount),
        memo=tx.memo
    )


@router.delete("/transactions/{tx_id}", tags=["Finance"])
def delete_transaction(tx_id: str, db: Session = Depends(get_db)):
    """가계부 거래 삭제 (내 거래 삭제)"""
    tx = db.query(FinanceTransaction).filter(FinanceTransaction.transaction_id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()
    return {"success": True, "message": "Transaction deleted successfully"}


@router.get("/summary", response_model=FinanceSummaryResponse, tags=["Finance"])
def get_finance_summary(
    user_id: Optional[str] = Query(None, description="사용자 ID로 필터링 (내 재무 요약)"),
    month: str = Query("2026-11", description="Year-Month e.g. 2026-11"),
    db: Session = Depends(get_db)
):
    """재무 요약 조회 (user_id 지정 시 해당 사용자의 요약만 조회)"""
    query = db.query(FinanceTransaction)
    if user_id:
        query = query.filter(FinanceTransaction.user_id == user_id)
    transactions = query.all()

    total_income = 0
    total_expense = 0
    category_sums = {
        "식비": 0,
        "육아/교육": 0,
        "주거/통신": 0,
        "쇼핑/생활": 0,
        "기타": 0
    }

    for tx in transactions:
        amount = int(tx.amount)
        if tx.transaction_type == "INCOME":
            total_income += amount
        else:
            total_expense += amount
            if tx.category_code in category_sums:
                category_sums[tx.category_code] += amount
            else:
                category_sums["기타"] += amount

    budget_limit = 3000000
    utilization_rate = round((total_expense / budget_limit) * 100, 1) if budget_limit > 0 else 0.0

    return FinanceSummaryResponse(
        month=month,
        total_income=total_income,
        total_expense=total_expense,
        net_savings=total_income - total_expense,
        budget_limit=budget_limit,
        budget_utilization_rate=utilization_rate,
        category_breakdown=category_sums
    )
