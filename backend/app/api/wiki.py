import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from backend.app.db.session import get_db
from backend.app.db.models import WikiDocument, WikiDocumentChunk
from backend.app.schemas.wiki import (
    WikiDocumentCreate, WikiDocumentResponse, WikiSearchResult
)
from backend.app.services.embedding_service import (
    generate_pseudo_embedding, chunk_markdown_text, cosine_similarity
)

router = APIRouter()

@router.get("/documents", response_model=List[WikiDocumentResponse])
def get_wiki_documents(
    category: str = Query(None, description="Optional category filter"),
    db: Session = Depends(get_db)
):
    query = db.query(WikiDocument).order_by(WikiDocument.created_at.desc())
    if category:
        query = query.filter(WikiDocument.category == category)
    
    docs = query.all()
    return [
        WikiDocumentResponse(
            id=doc.doc_id,
            title=doc.title,
            category=doc.category,
            content=doc.raw_markdown,
            date=doc.created_at.strftime("%Y-%m-%d"),
            version=doc.version
        )
        for doc in docs
    ]

@router.post("/documents", response_model=WikiDocumentResponse, status_code=201)
def create_wiki_document(
    doc_in: WikiDocumentCreate,
    db: Session = Depends(get_db)
):
    new_doc = WikiDocument(
        title=doc_in.title,
        category=doc_in.category,
        raw_markdown=doc_in.content,
        author_id=doc_in.author_id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Chunking & Vector Embedding for pgvector RAG
    chunks = chunk_markdown_text(doc_in.content)
    for idx, chunk_text in enumerate(chunks):
        emb = generate_pseudo_embedding(new_doc.title + " " + chunk_text)
        chunk_db = WikiDocumentChunk(
            doc_id=new_doc.doc_id,
            chunk_index=idx,
            chunk_text=chunk_text,
            embedding_json=json.dumps(emb)
        )
        db.add(chunk_db)
    db.commit()

    return WikiDocumentResponse(
        id=new_doc.doc_id,
        title=new_doc.title,
        category=new_doc.category,
        content=new_doc.raw_markdown,
        date=new_doc.created_at.strftime("%Y-%m-%d"),
        version=new_doc.version
    )

@router.get("/search", response_model=List[WikiSearchResult])
def search_wiki(
    q: str = Query(..., description="Search keyword or question"),
    limit: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    q_vec = generate_pseudo_embedding(q)
    chunks = db.query(WikiDocumentChunk).all()
    scored = []

    for c in chunks:
        try:
            emb = json.loads(c.embedding_json)
            score = cosine_similarity(q_vec, emb)
            scored.append(WikiSearchResult(
                doc_id=c.doc_id,
                title=c.document.title if c.document else "무제",
                category=c.document.category if c.document else "일반",
                matched_text=c.chunk_text,
                similarity_score=round(score, 3)
            ))
        except Exception:
            continue

    scored.sort(key=lambda x: x.similarity_score, reverse=True)
    return scored[:limit]

