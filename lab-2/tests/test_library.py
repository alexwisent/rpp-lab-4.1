"""Тесты доменной модели «Библиотека».

Запуск из папки lab-2:  python -m unittest -v
Используется стандартный unittest — ничего устанавливать не нужно.
"""

import unittest
from datetime import date
from decimal import Decimal

from library.adapters.memory import (
    InMemoryBookRepository,
    InMemoryLoanRepository,
    InMemoryReaderRepository,
)
from library.domain.aggregates import Book, LoanStatus, Reader
from library.domain.exceptions import DomainInvariantViolation, InvalidValueObject
from library.domain.services import CheckoutService, ReturnService
from library.domain.value_objects import (
    BookId,
    CatalogNumber,
    FullName,
    LoanPeriod,
    Money,
    ReaderId,
)


class LibraryTestCase(unittest.TestCase):
    def setUp(self):
        # Каждый тест получает свежую «базу» в памяти
        self.books = InMemoryBookRepository()
        self.readers = InMemoryReaderRepository()
        self.loans = InMemoryLoanRepository()
        self.checkout = CheckoutService(self.books, self.readers, self.loans)
        self.returns = ReturnService(self.books, self.loans)

        self.book = Book(BookId(1), CatalogNumber("И-101"), "Мастер и Маргарита", "Булгаков", 1)
        self.books.save(self.book)
        self.readers.save(Reader(ReaderId(1), FullName("Иванов Иван")))
        self.readers.save(Reader(ReaderId(2), FullName("Петрова Анна")))

    def issue(self, reader=1, day=1, days=14):
        return self.checkout.checkout(ReaderId(reader), BookId(1), date(2026, 11, day), days)

    # --- Инвариант 1 ---
    def test_checkout_decreases_available_copies(self):
        self.issue()
        self.assertEqual(self.book.available_copies, 0)

    def test_cannot_checkout_without_free_copies(self):
        self.issue(reader=1)
        with self.assertRaises(DomainInvariantViolation):
            self.issue(reader=2)

    # --- Инвариант 2 ---
    def test_cannot_return_without_open_loan(self):
        with self.assertRaises(DomainInvariantViolation):
            self.returns.return_book(ReaderId(1), BookId(1), date(2026, 11, 5))

    # --- Инвариант 3 ---
    def test_return_date_not_before_issue_date(self):
        loan = self.issue(day=10)
        with self.assertRaises(DomainInvariantViolation):
            loan.close(date(2026, 11, 9))

    # --- Инвариант 4: штраф всегда 1000 руб. ---
    def test_late_return_gives_fixed_fine(self):
        self.issue(day=1, days=14)                      # срок до 15.11
        fine = self.returns.return_book(ReaderId(1), BookId(1), date(2026, 12, 30))
        self.assertEqual(fine, Money(Decimal("1000")))

    def test_return_on_time_has_no_fine(self):
        self.issue(day=1, days=14)
        fine = self.returns.return_book(ReaderId(1), BookId(1), date(2026, 11, 15))
        self.assertEqual(fine, Money.zero())
        self.assertEqual(self.book.available_copies, 1)

    # --- Инвариант 5 ---
    def test_negative_money_is_impossible(self):
        with self.assertRaises(InvalidValueObject):
            Money(Decimal("-1"))

    # --- Инвариант 6 ---
    def test_due_date_not_before_issue_date(self):
        with self.assertRaises(InvalidValueObject):
            LoanPeriod(date(2026, 11, 10), date(2026, 11, 1))

    # --- Инвариант 7 ---
    def test_loan_cannot_be_closed_twice(self):
        loan = self.issue()
        loan.close(date(2026, 11, 5))
        self.assertEqual(loan.status, LoanStatus.CLOSED)
        with self.assertRaises(DomainInvariantViolation):
            loan.close(date(2026, 11, 6))

    # --- Состояние меняется только через методы ---
    def test_fields_are_read_only(self):
        with self.assertRaises(AttributeError):
            self.book.available_copies = 100

    def test_value_object_is_immutable(self):
        money = Money(Decimal("10"))
        with self.assertRaises(AttributeError):
            money.amount = Decimal("20")


if __name__ == "__main__":
    unittest.main()
