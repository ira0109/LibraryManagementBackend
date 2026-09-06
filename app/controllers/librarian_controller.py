from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import BookCreate, BookResponse, UserRegister, UserResponse, RequestResponse, RequestProcess, TransactionResponse
from app.models import User, RoleEnum
from app.dependencies import require_role
from app.repositories.book_repository import BookRepository
from app.repositories.request_repository import RequestRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.librarian_service import LibrarianService

router = APIRouter(prefix="/api/v1/librarian", tags=["Librarian Operations"])

def get_librarian_service(db: Session = Depends(get_db)) -> LibrarianService:
    return LibrarianService(
        BookRepository(db), RequestRepository(db), TransactionRepository(db), UserRepository(db)
    )

@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_data: BookCreate,
    _: User = Depends(require_role(RoleEnum.LIBRARIAN)),
    service: LibrarianService = Depends(get_librarian_service)
):
    return service.add_book(book_data)

@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_data: BookCreate,
    _: User = Depends(require_role(RoleEnum.LIBRARIAN)),
    service: LibrarianService = Depends(get_librarian_service)
):
    return service.update_book(book_id, book_data)

@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    _: User = Depends(require_role(RoleEnum.LIBRARIAN)),
    service: LibrarianService = Depends(get_librarian_service)
):
    service.delete_book(book_id)

@router.post("/members", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    user_data: UserRegister,
    _: User = Depends(require_role(RoleEnum.LIBRARIAN)),
    service: LibrarianService = Depends(get_librarian_service)
):
    return service.create_member_account(user_data)

@router.get("/members", response_model=List[UserResponse])
def get_members(
    _: User = Depends(require_role(RoleEnum.LIBRARIAN)),
    service: LibrarianService = Depends(get_librarian_service)
):
    return service.get_all_members()

@router.get("/queue", response_model=List[RequestResponse])
def get_queue(
    _: User = Depends(require_role(RoleEnum.LIBRARIAN)),
    service: LibrarianService = Depends(get_librarian_service)
):
    return service.get_pending_queue()

@router.post("/queue/{request_id}/process")
def process_queue(
    request_id: int,
    action: RequestProcess,
    background_tasks: BackgroundTasks,
    _: User = Depends(require_role(RoleEnum.LIBRARIAN)),
    service: LibrarianService = Depends(get_librarian_service)
):
    return service.process_queue_request(request_id, action, background_tasks)

@router.get("/book/{book_id}/history", response_model=List[TransactionResponse])
def get_book_history(
    book_id: int,
    _: User = Depends(require_role(RoleEnum.LIBRARIAN)),
    service: LibrarianService = Depends(get_librarian_service)
):
    return service.get_book_history(book_id)