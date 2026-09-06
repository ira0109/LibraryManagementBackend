import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class RoleEnum(str, enum.Enum):
    LIBRARIAN = "Librarian"
    MEMBER = "Member"

class AccountStatusEnum(str, enum.Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"

class BookStatusEnum(str, enum.Enum):
    AVAILABLE = "Available"
    ISSUED = "Issued"
    LOST = "Lost"

class RequestTypeEnum(str, enum.Enum):
    ISSUE = "Issue"
    RETURN = "Return"
    RENEW = "Renew"

class RequestStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.MEMBER, nullable=False)
    status = Column(SQLEnum(AccountStatusEnum), default=AccountStatusEnum.ACTIVE, nullable=False)

    requests = relationship("Request", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    isbn = Column(String(20), unique=True, nullable=False)
    genre = Column(String(50), nullable=False)
    status = Column(SQLEnum(BookStatusEnum), default=BookStatusEnum.AVAILABLE, nullable=False)

    requests = relationship("Request", back_populates="book")
    transactions = relationship("Transaction", back_populates="book")

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    type = Column(SQLEnum(RequestTypeEnum), nullable=False)
    status = Column(SQLEnum(RequestStatusEnum), default=RequestStatusEnum.PENDING, nullable=False)
    email_log_status = Column(String(50), default="Pending")

    user = relationship("User", back_populates="requests")
    book = relationship("Book", back_populates="requests")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    issue_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    due_date = Column(DateTime, nullable=False)
    actual_return_date = Column(DateTime, nullable=True)
    fines_accumulated = Column(Float, default=0.0, nullable=False)

    user = relationship("User", back_populates="transactions")
    book = relationship("Book", back_populates="transactions")