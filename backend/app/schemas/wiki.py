from typing import Optional, List
from pydantic import BaseModel

class WikiDocumentCreate(BaseModel):
    title: str
    category: str
    content: str
    author_id: Optional[str] = None

class WikiDocumentResponse(BaseModel):
    id: str
    title: str
    category: str
    content: str
    date: str
    version: int = 1

    class Config:
        from_attributes = True

class WikiSearchResult(BaseModel):
    doc_id: str
    title: str
    category: str
    matched_text: str
    similarity_score: float

