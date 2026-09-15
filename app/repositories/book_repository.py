from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Book, BookStatusEnum, Request, Transaction
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
            genre=book_data.genre,
            total_copies=book_data.total_copies,
            available_copies=book_data.total_copies,
            status=BookStatusEnum.AVAILABLE,
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
        issued_copies = book.total_copies - book.available_copies
        if book_data.total_copies < issued_copies:
            raise ValueError(
                f"Cannot reduce total copies below the {issued_copies} currently issued."
            )
        book.total_copies = book_data.total_copies
        book.available_copies = book_data.total_copies - issued_copies
        book.status = (
            BookStatusEnum.AVAILABLE
            if book.available_copies > 0
            else BookStatusEnum.ISSUED
        )

        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        """Delete a book and its non-active request/history records."""
        self.db.query(Request).filter(Request.book_id == book.id).delete(synchronize_session=False)
        self.db.query(Transaction).filter(Transaction.book_id == book.id).delete(synchronize_session=False)
        self.db.delete(book)
        self.db.commit()

    def has_history(self, book_id: int) -> bool:
        return self.db.query(Transaction.id).filter(Transaction.book_id == book_id).first() is not None

    def has_requests(self, book_id: int) -> bool:
        return self.db.query(Request.id).filter(Request.book_id == book_id).first() is not None