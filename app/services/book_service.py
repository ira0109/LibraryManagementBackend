from typing import List, Optional
from app.models import Book
from app.repositories.book_repository import BookRepository

class BookService:
    def __init__(self, book_repo: BookRepository):
        self.book_repo = book_repo

    def search_books(self, title: Optional[str], author: Optional[str], genre: Optional[str]) -> List[Book]:
        return self.book_repo.search(title, author, genre)