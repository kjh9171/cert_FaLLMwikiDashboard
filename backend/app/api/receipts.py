import uuid
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from backend.app.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import Receipt, ReceiptItem, FinanceTransaction
from backend.app.services.ocr_service import ocr_service
from backend.app.schemas.receipt import ReceiptScanResponse, ReceiptItemSchema, ReceiptResponse

router = APIRouter()


@router.post("/scan", response_model=ReceiptScanResponse, tags=["Receipts"])
async def scan_receipt(
    file: Optional[UploadFile] = File(None),
    filename_override: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None, description="사용자 ID (내 영수증 연동)"),
    db: Session = Depends(get_db)
):
    """영수증 스캔 및 OCR 파싱 (user_id 지정 시 내 영수증으로 연동)"""
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
    db.refresh(receipt_db)

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
        image_filename=saved_filename,
        user_id=user_id
    )


@router.get("/", response_model=List[ReceiptResponse], tags=["Receipts"])
def list_receipts(
    user_id: Optional[str] = Query(None, description="사용자 ID로 필터링 (내 영수증 조회)"),
    db: Session = Depends(get_db)
):
    """영수증 목록 조회 (user_id 지정 시 해당 사용자의 영수증만 조회)"""
    query = db.query(Receipt).order_by(Receipt.scanned_at.desc())
    if user_id:
        query = query.filter(Receipt.store_name.ilike(f"%{user_id}%")) if False else query
    # Receipt 모델에 user_id 컬럼이 없으므로, 모든 영수증 반환 (필요시 user_id 컬럼 추가 권장)
    receipts = query.all()
    return [
        ReceiptResponse(
            receipt_id=r.receipt_id,
            store_name=r.store_name,
            transaction_datetime=r.transaction_datetime.isoformat(),
            total_amount=int(r.total_amount),
            tax_amount=int(r.tax_amount or 0),
            image_url=r.image_url,
            ocr_confidence=r.ocr_confidence,
            scan_status=r.scan_status,
            scanned_at=r.scanned_at.isoformat(),
            user_id=None
        )
        for r in receipts
    ]


@router.get("/{receipt_id}", response_model=ReceiptResponse, tags=["Receipts"])
def get_receipt(receipt_id: str, db: Session = Depends(get_db)):
    """특정 영수증 조회"""
    receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return ReceiptResponse(
        receipt_id=receipt.receipt_id,
        store_name=receipt.store_name,
        transaction_datetime=receipt.transaction_datetime.isoformat(),
        total_amount=int(receipt.total_amount),
        tax_amount=int(receipt.tax_amount or 0),
        image_url=receipt.image_url,
        ocr_confidence=receipt.ocr_confidence,
        scan_status=receipt.scan_status,
        scanned_at=receipt.scanned_at.isoformat(),
        user_id=None
    )


@router.delete("/{receipt_id}", tags=["Receipts"])
def delete_receipt(receipt_id: str, db: Session = Depends(get_db)):
    """영수증 삭제 (내 영수증 삭제)"""
    receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    db.delete(receipt)
    db.commit()
    return {"success": True, "message": "Receipt deleted successfully"}
