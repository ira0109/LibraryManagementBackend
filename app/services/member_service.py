from fastapi import HTTPException, BackgroundTasks, status
from app.models import User, Request, RoleEnum, RequestTypeEnum, RequestStatusEnum
from app.schemas import RequestCreate
from app.repositories.book_repository import BookRepository
from app.repositories.request_repository import RequestRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.mail_service import MailService

class MemberService:
    def __init__(
        self, 
        book_repo: BookRepository, 
        request_repo: RequestRepository, 
        trans_repo: TransactionRepository,
        user_repo: UserRepository
    ):
        self.book_repo = book_repo
        self.request_repo = request_repo
        self.trans_repo = trans_repo
        self.user_repo = user_repo

    def submit_request(self, req_data: RequestCreate, current_user: User, background_tasks: BackgroundTasks) -> Request:
        book = self.book_repo.get_by_id(req_data.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Requested book does not exist.")

        # Step 2: System Validation Check
        if req_data.type == RequestTypeEnum.ISSUE:
            if book.available_copies <= 0:
                background_tasks.add_task(
                    MailService.send_automated_email,
                    current_user.email,
                    "Library Request Failed: System Validation Issue",
                    f"Hi {current_user.name}, Your request for '{book.title}' could not be processed because it is currently unavailable."
                )
                raise HTTPException(status_code=400, detail="Book is not available for issue.")

            active_count = self.trans_repo.count_active_loans_by_user(current_user.id)
            if active_count >= 3:
                background_tasks.add_task(
                    MailService.send_automated_email,
                    current_user.email,
                    "Library Request Failed: System Validation Issue",
                    f"Hi {current_user.name}, Your request for '{book.title}' could not be processed because you reached your maximum active loan limit (3 books)."
                )
                raise HTTPException(status_code=400, detail="Maximum borrowing cap reached (3 active loans).")

        # Step 1: Request Submission Execution
        new_request = Request(
            user_id=current_user.id,
            book_id=book.id,
            type=req_data.type,
            status=RequestStatusEnum.PENDING,
            email_log_status="Ack_Sent"
        )
        created_request = self.request_repo.create(new_request)

        # Notify Librarians (Email 1)
        librarians = self.user_repo.get_by_role(RoleEnum.LIBRARIAN)
        for lib in librarians:
            background_tasks.add_task(
                MailService.send_automated_email,
                lib.email,
                f"[Action Required] New Book Request Received - Request ID #{created_request.id}",
                f"Hello Admin, User {current_user.name} (ID: {current_user.id}) submitted a request to {req_data.type.value} '{book.title}'."
            )

        # Acknowledge Member (Email 2)
        background_tasks.add_task(
            MailService.send_automated_email,
            current_user.email,
            "Library Request Received - Pending Review",
            f"Hi {current_user.name}, We received your request for '{book.title}'. It is in the librarian queue awaiting confirmation."
        )

        return created_request

    def get_dashboard_data(self, current_user: User) -> dict:
        active_loans = self.trans_repo.get_active_loans_by_user(current_user.id)
        pending_requests = self.request_repo.get_pending_by_user(current_user.id)
        return {"active_loans": active_loans, "pending_requests": pending_requests}