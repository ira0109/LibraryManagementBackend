from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import Transaction

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_loans_by_user(self, user_id: int) -> List[Transaction]:
        return self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.actual_return_date == None
        ).all()

    def count_active_loans_by_user(self, user_id: int) -> int:
        return self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.actual_return_date == None
        ).count()

    def get_active_loan_by_user_and_book(self, user_id: int, book_id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.book_id == book_id,
            Transaction.actual_return_date == None
        ).first()

    def get_by_book_id(self, book_id: int) -> List[Transaction]:
        return self.db.query(Transaction).filter(Transaction.book_id == book_id).all()

    def get_by_user_id(self, user_id: int) -> List[Transaction]:
        return self.db.query(Transaction).filter(Transaction.user_id == user_id).all()

    def get_history_by_book(self, book_id: int) -> List[Transaction]:
        return self.get_by_book_id(book_id)

    def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update(self, transaction: Transaction) -> Transaction:
        self.db.commit()
        self.db.refresh(transaction)
        return transaction