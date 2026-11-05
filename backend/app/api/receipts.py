import uuid
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
from datetime import datetime

from backend.app.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import Receipt, ReceiptItem
from backend.app.services.ocr_service import ocr_service
from backend.app.schemas.receipt import ReceiptScanResponse, ReceiptItemSchema

router = APIRouter()

@router.post("/scan", response_model=ReceiptScanResponse)
async def scan_receipt(
    file: Optional[UploadFile] = File(None),
    filename_override: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    saved_filename = "demo_receipt.jpg"
    target_path = settings.UPLOAD_DIR / saved_filename

    if file:
        original_name = file.filename or "receipt.jpg"
        file_ext = Path(original_name).suffix or ".jpg"
        saved_filename = f"rcpt_{uuid.uuid4().hex[:8]}{file_ext}"
        target_path = settings.UPLOAD_DIR / saved_filename
        
        async with aiofiles.open(target_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
    elif filename_override:
        saved_filename = filename_override

    # OCR Parsing Execution
    parsed = ocr_service.parse_receipt_image(target_path, saved_filename)

    # Save to Database as Pending/Parsed Receipt
    receipt_db = Receipt(
        receipt_id=f"rcpt_{uuid.uuid4().hex[:8]}",
        store_name=parsed["store_name"],
        transaction_datetime=datetime.now(),
        total_amount=parsed["total_amount"],
        tax_amount=parsed["tax_amount"],
        image_url=f"/uploads/{saved_filename}",
        ocr_confidence=parsed["ocr_confidence"],
        scan_status="PARSED"
    )
    db.add(receipt_db)
    db.commit()

    # Add detail items
    for item in parsed["items"]:
        item_db = ReceiptItem(
            receipt_id=receipt_db.receipt_id,
            item_name=item["name"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            total_price=item["total_price"]
        )
        db.add(item_db)
    db.commit()

    return ReceiptScanResponse(
        receipt_id=receipt_db.receipt_id,
        store_name=parsed["store_name"],
        scanned_at=parsed["transaction_datetime"],
        total_amount=parsed["total_amount"],
        tax_amount=parsed["tax_amount"],
        items=[ReceiptItemSchema(**item) for item in parsed["items"]],
        recommended_category=parsed["recommended_category"],
        ocr_confidence=parsed["ocr_confidence"],
        image_filename=saved_filename
    )

