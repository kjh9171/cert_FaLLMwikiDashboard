from typing import List, Optional
from pydantic import BaseModel


class ReceiptItemSchema(BaseModel):
    name: str
    quantity: int = 1
    unit_price: int
    total_price: int


class ReceiptScanResponse(BaseModel):
    receipt_id: str
    store_name: str
    scanned_at: str
    total_amount: int
    tax_amount: int
    items: List[ReceiptItemSchema]
    recommended_category: str
    ocr_confidence: float
    image_filename: Optional[str] = None
    user_id: Optional[str] = None


class ReceiptResponse(BaseModel):
    receipt_id: str
    store_name: str
    transaction_datetime: str
    total_amount: int
    tax_amount: int
    image_url: Optional[str] = None
    ocr_confidence: float
    scan_status: str
    scanned_at: str
    user_id: Optional[str] = None

    class Config:
        from_attributes = True
