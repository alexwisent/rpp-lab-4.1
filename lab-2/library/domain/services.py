"""Доменные сервисы библиотеки.

Выдача и возврат меняют сразу два агрегата (Book и Loan),
поэтому не могут быть методом ни одного из них.
Сервис только координирует: загружает агрегаты через репозитории
и вызывает их собственные методы — сам состояние не меняет.
"""

from datetime import date

from .aggregates import Loan
from .exceptions import DomainInvariantViolation
from .repositories import BookRepository, LoanRepository, ReaderRepository
from .value_objects import BookId, LoanPeriod, Money, ReaderId


class CheckoutService:
    """Выдать книгу читателю."""

    def __init__(self, books: BookRepository, readers: ReaderRepository,
                 loans: LoanRepository) -> None:
        self._books = books
        self._readers = readers
        self._loans = loans

    def checkout(self, reader_id: ReaderId, book_id: BookId,
                 issue_date: date, days: int) -> Loan:
        self._readers.get(reader_id)          # читатель должен существовать
        book = self._books.get(book_id)
        period = LoanPeriod.starting(issue_date, days)

        book.take_copy()                      # инвариант 1 проверяет сама книга
        loan = Loan(self._loans.next_id(), book.id, reader_id, period)

        self._books.save(book)
        self._loans.save(loan)
        return loan


class ReturnService:
    """Принять книгу от читателя."""

    def __init__(self, books: BookRepository, loans: LoanRepository) -> None:
        self._books = books
        self._loans = loans

    def return_book(self, reader_id: ReaderId, book_id: BookId,
                    return_date: date) -> Money:
        # Инвариант 2: должна существовать незакрытая выдача
        loan = self._loans.find_open(reader_id, book_id)
        if loan is None:
            raise DomainInvariantViolation(
                "У этого читателя нет открытой выдачи этой книги")

        fine = loan.close(return_date)        # инварианты 3, 4, 7 — внутри Loan
        book = self._books.get(loan.book_id)
        book.put_copy_back()

        self._loans.save(loan)
        self._books.save(book)
        return fine
