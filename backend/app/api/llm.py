from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.llm_service import llm_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_family_llm(
    req: ChatRequest,
    db: Session = Depends(get_db)
):
    result = await llm_service.generate_response(db, req.prompt)
    return ChatResponse(
        answer=result["answer"],
        retrieved_context=result["retrieved_context"],
        tool_call=result["tool_call"],
        timestamp=result["timestamp"]
    )

