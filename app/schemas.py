from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from app.models import RoleEnum, AccountStatusEnum, BookStatusEnum, RequestTypeEnum, RequestStatusEnum

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[RoleEnum] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    status: AccountStatusEnum

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    genre: str

class BookResponse(BookCreate):
    id: int
    status: BookStatusEnum

    class Config:
        from_attributes = True

class RequestCreate(BaseModel):
    book_id: int
    type: RequestTypeEnum

class RequestResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    type: RequestTypeEnum
    status: RequestStatusEnum
    email_log_status: str

    class Config:
        from_attributes = True

class RequestProcess(BaseModel):
    approve: bool
    rejection_reason: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    issue_date: datetime
    due_date: datetime
    actual_return_date: Optional[datetime]
    fines_accumulated: float

    class Config:
        from_attributes = True

class MemberDashboardResponse(BaseModel):
    active_loans: List[TransactionResponse]
    pending_requests: List[RequestResponse]