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

