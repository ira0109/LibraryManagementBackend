from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.models import Request, RequestStatusEnum, RequestTypeEnum, BookStatusEnum, Transaction, User, Book
from app.services.mail_service import MailService

class RequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, request_id: int) -> Optional[Request]:
        return self.db.query(Request).filter(Request.id == request_id).first()

    def get_pending_by_user(self, user_id: int) -> List[Request]:
        return self.db.query(Request).filter(
            Request.user_id == user_id,
            Request.status == RequestStatusEnum.PENDING
        ).all()

    def get_all_pending(self) -> List[Request]:
        return self.db.query(Request).filter(Request.status == RequestStatusEnum.PENDING).all()

    def get_pending_requests(self) -> List[Request]:
        return self.get_all_pending()

    def create(self, request: Request) -> Request:
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def update(self, request: Request) -> Request:
        self.db.commit()
        self.db.refresh(request)
        return request

    def process_request(self, request: Request, action, background_tasks: Optional[BackgroundTasks] = None) -> Request:
        now = datetime.now(timezone.utc)
        if action.approve:
            request.status = RequestStatusEnum.APPROVED
            request.email_log_status = "Approved"

            if request.type == RequestTypeEnum.ISSUE:
                request.book.status = BookStatusEnum.ISSUED
                existing_tx = self.db.query(Transaction).filter(
                    Transaction.user_id == request.user_id,
                    Transaction.book_id == request.book_id,
                    Transaction.actual_return_date == None,
                ).first()
                if not existing_tx:
                    self.db.add(
                        Transaction(
                            user_id=request.user_id,
                            book_id=request.book_id,
                            due_date=now + timedelta(days=14),
                        )
                    )
            elif request.type == RequestTypeEnum.RETURN:
                request.book.status = BookStatusEnum.AVAILABLE
                active_tx = self.db.query(Transaction).filter(
                    Transaction.user_id == request.user_id,
                    Transaction.book_id == request.book_id,
                    Transaction.actual_return_date == None,
                ).order_by(Transaction.issue_date.desc()).first()
                if active_tx:
                    active_tx.actual_return_date = now
            elif request.type == RequestTypeEnum.RENEW:
                active_tx = self.db.query(Transaction).filter(
                    Transaction.user_id == request.user_id,
                    Transaction.book_id == request.book_id,
                    Transaction.actual_return_date == None,
                ).order_by(Transaction.issue_date.desc()).first()
                if active_tx:
                    active_tx.due_date = active_tx.due_date + timedelta(days=14)
        else:
            request.status = RequestStatusEnum.REJECTED
            request.email_log_status = "Rejected"
            if request.type == RequestTypeEnum.ISSUE:
                request.book.status = BookStatusEnum.AVAILABLE

        self.db.commit()
        self.db.refresh(request)

        if background_tasks:
            member = self.db.query(User).filter(User.id == request.user_id).first()
            book = self.db.query(Book).filter(Book.id == request.book_id).first()
            member_name = member.name if member else "Member"
            member_email = member.email if member else None
            book_title = book.title if book else "your requested book"
            action_label = "Approved" if action.approve else "Rejected"
            reason_suffix = f" Reason: {getattr(action, 'rejection_reason', None) or 'No reason provided'}" if not action.approve and getattr(action, 'rejection_reason', None) else ""
            if member_email:
                background_tasks.add_task(
                    MailService.send_automated_email,
                    member_email,
                    f"Library Request {action_label} - Request ID #{request.id}",
                    f"Hi {member_name}, your request for '{book_title}' has been {action_label.lower()}.{reason_suffix}"
                )

        return request