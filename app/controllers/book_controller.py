from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import BookResponse
from app.models import User
from app.dependencies import get_current_user
from app.repositories.book_repository import BookRepository
from app.services.book_service import BookService

router = APIRouter(prefix="/api/v1/books", tags=["Catalog Search"])

@router.get("", response_model=List[BookResponse])
def search_books(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    book_service = BookService(BookRepository(db))
    return book_service.search_books(title, author, genre)