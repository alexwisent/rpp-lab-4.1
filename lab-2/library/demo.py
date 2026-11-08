"""Демонстрация доменной модели «Библиотека».

Запуск из папки lab-2:  python -m library.demo
"""

from datetime import date
from decimal import Decimal

from library.adapters.memory import (
    InMemoryBookRepository,
    InMemoryLoanRepository,
    InMemoryReaderRepository,
)
from library.domain.aggregates import Book, Reader
from library.domain.exceptions import DomainError
from library.domain.services import CheckoutService, ReturnService
from library.domain.value_objects import (
    BookId,
    CatalogNumber,
    FullName,
    LoanPeriod,
    Money,
    ReaderId,
)


def try_action(title, action):
    """Выполнить действие и показать результат или доменную ошибку."""
    try:
        result = action()
        print(f"  [OK]     {title}: {result}")
    except DomainError as error:
        print(f"  [ОТКАЗ]  {title}: {type(error).__name__}: {error}")


def main() -> None:
    # «База данных» в памяти
    books = InMemoryBookRepository()
    readers = InMemoryReaderRepository()
    loans = InMemoryLoanRepository()

    checkout = CheckoutService(books, readers, loans)
    returns = ReturnService(books, loans)

    # Исходные данные
    book = Book(BookId(1), CatalogNumber("И-101"), "Мастер и Маргарита", "М. Булгаков", 1)
    books.save(book)
    readers.save(Reader(ReaderId(1), FullName("Иванов Иван")))
    readers.save(Reader(ReaderId(2), FullName("Петрова Анна")))

    print("=== Библиотека ===")
    print("Книга:", book)

    print("\n1. Выдача книги")
    try_action("Иванов берёт книгу на 14 дней",
               lambda: checkout.checkout(ReaderId(1), BookId(1), date(2026, 11, 1), 14))
    print("  Книга после выдачи:", book)

    print("\n2. Инвариант 1: нет свободных экземпляров")
    try_action("Петрова берёт ту же книгу",
               lambda: checkout.checkout(ReaderId(2), BookId(1), date(2026, 11, 2), 14))

    print("\n3. Инвариант 2: возврат без открытой выдачи")
    try_action("Петрова возвращает книгу, которую не брала",
               lambda: returns.return_book(ReaderId(2), BookId(1), date(2026, 11, 5)))

    print("\n4. Инвариант 3: дата возврата раньше даты выдачи")
    try_action("Иванов возвращает книгу 31.10.26",
               lambda: returns.return_book(ReaderId(1), BookId(1), date(2026, 10, 31)))

    print("\n5. Инвариант 4: возврат с просрочкой -> штраф 1000 руб.")
    try_action("Иванов возвращает книгу 20.11.26 (срок до 15.11.26)",
               lambda: returns.return_book(ReaderId(1), BookId(1), date(2026, 11, 20)))
    print("  Книга после возврата:", book)

    print("\n6. Инвариант 7: повторное закрытие той же выдачи")
    closed_loan = loans.all()[0]
    try_action("Закрыть выдачу №1 ещё раз",
               lambda: closed_loan.close(date(2026, 11, 21)))

    print("\n7. Возврат вовремя -> штраф 0 руб.")
    try_action("Петрова берёт книгу на 7 дней",
               lambda: checkout.checkout(ReaderId(2), BookId(1), date(2026, 11, 21), 7))
    try_action("Петрова возвращает книгу 25.11.26",
               lambda: returns.return_book(ReaderId(2), BookId(1), date(2026, 11, 25)))

    print("\n8. Инварианты 5 и 6: объекты-значения не создаются с плохими данными")
    try_action("Штраф -500 руб.", lambda: Money(Decimal("-500")))
    try_action("Срок возврата раньше выдачи",
               lambda: LoanPeriod(date(2026, 11, 10), date(2026, 11, 1)))
    try_action("ID книги = 0", lambda: BookId(0))
    try_action("ФИО из одного слова", lambda: FullName("Иванов"))

    print("\nВсе выдачи:")
    for loan in loans.all():
        print("  ", loan)


if __name__ == "__main__":
    main()
