from typing import List
from fastapi import HTTPException, status, BackgroundTasks
from app.models import User, RoleEnum, AccountStatusEnum
from app.repositories.book_repository import BookRepository
from app.repositories.request_repository import RequestRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.schemas import BookCreate, RequestProcess, UserRegister
from app.services.auth_service import AuthService

class LibrarianService:
    def __init__(
        self,
        book_repo: BookRepository,
        request_repo: RequestRepository,
        transaction_repo: TransactionRepository,
        user_repo: UserRepository
    ):
        self.book_repo = book_repo
        self.request_repo = request_repo
        self.transaction_repo = transaction_repo
        self.user_repo = user_repo

    def add_book(self, book_data: BookCreate):
        return self.book_repo.create(book_data)

    def update_book(self, book_id: int, book_data: BookCreate):
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} was not found."
            )
        return self.book_repo.update(book, book_data)

    def delete_book(self, book_id: int):
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} was not found."
            )
        self.book_repo.delete(book)

    def create_member_account(self, user_data: UserRegister):
        requested_role = user_data.role or RoleEnum.MEMBER
        if requested_role not in (RoleEnum.MEMBER, RoleEnum.LIBRARIAN):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Member and Librarian roles are allowed."
            )

        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )

        auth_service = AuthService(self.user_repo)
        member = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=auth_service.hash_password(user_data.password),
            role=requested_role,
            status=AccountStatusEnum.ACTIVE,
        )
        return self.user_repo.create(member)

    def get_all_members(self):
        return self.user_repo.get_all_members()

    def get_pending_queue(self):
        return self.request_repo.get_pending_requests()

    def process_queue_request(self, request_id: int, action: RequestProcess, background_tasks: BackgroundTasks):
        req = self.request_repo.get_by_id(request_id)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request with ID {request_id} not found."
            )
        # Add your custom approval logic here
        return self.request_repo.process_request(req, action, background_tasks)

    def get_book_history(self, book_id: int):
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found."
            )
        return self.transaction_repo.get_by_book_id(book_id)