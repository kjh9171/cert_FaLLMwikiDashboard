from datetime import date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class TransactionCreate(BaseModel):
    user_id: Optional[str] = None
    type: str = Field(..., description="EXPENSE or INCOME")
    title: str
    amount: int = Field(..., gt=0)
    category: str
    transaction_date: Optional[date] = None
    payment_method: str = "신한카드"
    memo: Optional[str] = None
    receipt_id: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    date: str
    type: str
    title: str
    category: str
    method: str
    amount: int
    memo: Optional[str] = None

    class Config:
        from_attributes = True

class CategoryBreakdownItem(BaseModel):
    category: str
    amount: int
    percentage: float

class FinanceSummaryResponse(BaseModel):
    month: str
    total_income: int
    total_expense: int
    net_savings: int
    budget_limit: int
    budget_utilization_rate: float
    category_breakdown: Dict[str, int]

