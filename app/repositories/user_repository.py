from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import User, RoleEnum, Request, Transaction

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_role(self, role: RoleEnum) -> List[User]:
        return self.db.query(User).filter(User.role == role).all()

    def get_all_members(self) -> List[User]:
        return self.db.query(User).filter(User.role == RoleEnum.MEMBER).all()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def has_history(self, user_id: int) -> bool:
        return self.db.query(Transaction.id).filter(Transaction.user_id == user_id).first() is not None

    def has_requests(self, user_id: int) -> bool:
        return self.db.query(Request.id).filter(Request.user_id == user_id).first() is not None

    def delete(self, user: User) -> None:
        self.db.query(Request).filter(Request.user_id == user.id).delete(synchronize_session=False)
        self.db.query(Transaction).filter(Transaction.user_id == user.id).delete(synchronize_session=False)
        self.db.delete(user)
        self.db.commit()