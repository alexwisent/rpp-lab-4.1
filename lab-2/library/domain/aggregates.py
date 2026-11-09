"""Агрегаты библиотеки: Book, Loan, Reader.

Правила:
- состояние хранится в «закрытых» полях (с подчёркиванием),
  снаружи доступно только для чтения через @property;
- изменить состояние можно только методами корня агрегата,
  и эти методы проверяют инварианты.
"""

from datetime import date
from enum import Enum

from .exceptions import DomainInvariantViolation, InvalidValueObject
from .value_objects import (
    LATE_RETURN_FINE,
    BookId,
    CatalogNumber,
    FullName,
    LoanId,
    LoanPeriod,
    Money,
    ReaderId,
)


class Book:
    """Корень агрегата «Книга»: счётчик экземпляров.

    Инвариант 1: нельзя выдать книгу, если нет свободных экземпляров
    (доступных экземпляров всегда от 0 до общего количества).
    """

    def __init__(self, book_id: BookId, catalog_number: CatalogNumber,
                 title: str, author: str, total_copies: int) -> None:
        if not title.strip() or not author.strip():
            raise InvalidValueObject("Название и автор книги обязательны")
        if not isinstance(total_copies, int) or total_copies <= 0:
            raise DomainInvariantViolation("У книги должен быть хотя бы один экземпляр")
        self._id = book_id
        self._catalog_number = catalog_number
        self._title = title
        self._author = author
        self._total_copies = total_copies
        self._available_copies = total_copies  # сначала все экземпляры на полке

    # --- только чтение ---
    @property
    def id(self) -> BookId:
        return self._id

    @property
    def catalog_number(self) -> CatalogNumber:
        return self._catalog_number

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def total_copies(self) -> int:
        return self._total_copies

    @property
    def available_copies(self) -> int:
        return self._available_copies

    # --- поведение ---
    def take_copy(self) -> None:
        """Забрать экземпляр с полки (при выдаче читателю)."""
        if self._available_copies == 0:
            raise DomainInvariantViolation(
                f"Нет свободных экземпляров книги «{self._title}»")
        self._available_copies -= 1

    def put_copy_back(self) -> None:
        """Вернуть экземпляр на полку (при возврате)."""
        if self._available_copies == self._total_copies:
            raise DomainInvariantViolation(
                "Все экземпляры уже на полке — возвращать нечего")
        self._available_copies += 1

    def __repr__(self) -> str:
        return (f"Book(id={self._id.value}, «{self._title}», {self._author}, "
                f"доступно {self._available_copies}/{self._total_copies})")


class LoanStatus(Enum):
    ISSUED = "Выдан"
    CLOSED = "Закрыта"


class Loan:
    """Корень агрегата «Выдача».

    Хранит только идентификаторы книги и читателя (book_id, reader_id),
    а не сами объекты — связь между агрегатами по ID.

    Инварианты:
    3 — дата возврата не раньше даты выдачи;
    4 — при просрочке штраф (1000 руб.) рассчитывается и фиксируется;
    7 — одну выдачу нельзя закрыть дважды.
    """

    def __init__(self, loan_id: LoanId, book_id: BookId,
                 reader_id: ReaderId, period: LoanPeriod) -> None:
        self._id = loan_id
        self._book_id = book_id
        self._reader_id = reader_id
        self._period = period
        self._status = LoanStatus.ISSUED
        self._returned_on: date | None = None
        self._fine = Money.zero()

    @property
    def id(self) -> LoanId:
        return self._id

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def reader_id(self) -> ReaderId:
        return self._reader_id

    @property
    def period(self) -> LoanPeriod:
        return self._period

    @property
    def status(self) -> LoanStatus:
        return self._status

    @property
    def returned_on(self) -> date | None:
        return self._returned_on

    @property
    def fine(self) -> Money:
        return self._fine

    @property
    def is_open(self) -> bool:
        return self._status is LoanStatus.ISSUED

    def close(self, return_date: date) -> Money:
        """Закрыть выдачу возвратом. Возвращает начисленный штраф."""
        # Инвариант 7
        if self._status is LoanStatus.CLOSED:
            raise DomainInvariantViolation("Выдача уже закрыта возвратом")
        # Инвариант 3
        if return_date < self._period.issue_date:
            raise DomainInvariantViolation("Дата возврата не может быть раньше даты выдачи")
        # Инвариант 4: штраф фиксируется в момент закрытия
        if self._period.is_overdue_on(return_date):
            self._fine = LATE_RETURN_FINE
        self._returned_on = return_date
        self._status = LoanStatus.CLOSED
        return self._fine

    def __repr__(self) -> str:
        returned = f", возврат {self._returned_on:%d.%m.%y}" if self._returned_on else ""
        return (f"Loan(id={self._id.value}, книга={self._book_id.value}, "
                f"читатель={self._reader_id.value}, срок {self._period}, "
                f"{self._status.value}{returned}, штраф {self._fine})")


class Reader:
    """Корень агрегата «Читатель». Простой агрегат: ID + ФИО."""

    def __init__(self, reader_id: ReaderId, full_name: FullName) -> None:
        self._id = reader_id
        self._full_name = full_name

    @property
    def id(self) -> ReaderId:
        return self._id

    @property
    def full_name(self) -> FullName:
        return self._full_name

    def __repr__(self) -> str:
        return f"Reader(id={self._id.value}, {self._full_name.value})"
