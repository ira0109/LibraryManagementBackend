from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Book
from app.schemas import BookCreate

class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Fetch a book by primary key 'id'."""
        return self.db.query(Book).filter(Book.id == book_id).first()

    def search(self, title: Optional[str], author: Optional[str], genre: Optional[str]) -> List[Book]:
        query = self.db.query(Book)
        if title:
            query = query.filter(Book.title.ilike(f"%{title}%"))
        if author:
            query = query.filter(Book.author.ilike(f"%{author}%"))
        if genre:
            query = query.filter(Book.genre.ilike(f"%{genre}%"))
        return query.order_by(Book.id).all()

    def create(self, book_data: BookCreate) -> Book:
        """Create and commit a new book."""
        db_book = Book(
            title=book_data.title,
            author=book_data.author,
            isbn=book_data.isbn,
            genre=book_data.genre
        )
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    def update(self, book: Book, book_data: BookCreate) -> Book:
        """Update existing book record fields."""
        book.title = book_data.title
        book.author = book_data.author
        book.isbn = book_data.isbn
        book.genre = book_data.genre

        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        """Delete a book record."""
        self.db.delete(book)
        self.db.commit()