from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    prompt: str
    enable_agent_action: bool = True

class ChatResponse(BaseModel):
    answer: str
    retrieved_context: List[Dict[str, Any]] = []
    tool_call: Optional[Dict[str, Any]] = None
    timestamp: str

