"""In-memory реализации репозиториев (адаптеры).

Вместо базы данных — обычные словари Python.
Классы не наследуются от Protocol: им достаточно иметь
методы с нужными именами и параметрами.
"""

from library.domain.aggregates import Book, Loan, Reader
from library.domain.exceptions import AggregateNotFound
from library.domain.value_objects import BookId, LoanId, ReaderId


class InMemoryBookRepository:
    def __init__(self) -> None:
        self._items: dict[BookId, Book] = {}

    def get(self, book_id: BookId) -> Book:
        if book_id not in self._items:
            raise AggregateNotFound(f"Книга {book_id.value} не найдена")
        return self._items[book_id]

    def save(self, book: Book) -> None:
        self._items[book.id] = book


class InMemoryReaderRepository:
    def __init__(self) -> None:
        self._items: dict[ReaderId, Reader] = {}

    def get(self, reader_id: ReaderId) -> Reader:
        if reader_id not in self._items:
            raise AggregateNotFound(f"Читатель {reader_id.value} не найден")
        return self._items[reader_id]

    def save(self, reader: Reader) -> None:
        self._items[reader.id] = reader


class InMemoryLoanRepository:
    def __init__(self) -> None:
        self._items: dict[LoanId, Loan] = {}
        self._last_id = 0

    def next_id(self) -> LoanId:
        # Уникальный ID > 0: просто счётчик
        self._last_id += 1
        return LoanId(self._last_id)

    def get(self, loan_id: LoanId) -> Loan:
        if loan_id not in self._items:
            raise AggregateNotFound(f"Выдача {loan_id.value} не найдена")
        return self._items[loan_id]

    def save(self, loan: Loan) -> None:
        self._items[loan.id] = loan

    def find_open(self, reader_id: ReaderId, book_id: BookId) -> Loan | None:
        for loan in self._items.values():
            if loan.is_open and loan.reader_id == reader_id and loan.book_id == book_id:
                return loan
        return None

    def all(self) -> list[Loan]:
        return list(self._items.values())
