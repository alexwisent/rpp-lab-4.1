"""Порты репозиториев (Protocol).

Домен описывает только, ЧТО ему нужно от хранилища.
КАК это хранится (словарь в памяти или настоящая БД) — дело адаптера.
Один репозиторий — на один агрегат.
"""

from typing import Protocol

from .aggregates import Book, Loan, Reader
from .value_objects import BookId, LoanId, ReaderId


class BookRepository(Protocol):
    def get(self, book_id: BookId) -> Book: ...
    def save(self, book: Book) -> None: ...


class ReaderRepository(Protocol):
    def get(self, reader_id: ReaderId) -> Reader: ...
    def save(self, reader: Reader) -> None: ...


class LoanRepository(Protocol):
    def next_id(self) -> LoanId: ...
    def get(self, loan_id: LoanId) -> Loan: ...
    def save(self, loan: Loan) -> None: ...

    # Инвариант 2 — это условие поиска: открытая выдача этой книги этому читателю
    def find_open(self, reader_id: ReaderId, book_id: BookId) -> Loan | None: ...
