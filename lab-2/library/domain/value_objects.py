"""Объекты-значения библиотеки.

Все объекты-значения неизменяемы (frozen=True), сравниваются по значению
и проверяют свои данные в __post_init__: некорректный объект
просто не может быть создан.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from .exceptions import InvalidValueObject


# ---------- Идентификаторы ----------
# Каждый идентификатор — отдельный тип, поэтому BookId нельзя
# случайно передать туда, где ожидается ReaderId.

@dataclass(frozen=True)
class BookId:
    value: int

    def __post_init__(self) -> None:
        # ID — уникальное целое число > 0
        if not isinstance(self.value, int) or self.value <= 0:
            raise InvalidValueObject("ID книги должен быть целым числом > 0")


@dataclass(frozen=True)
class ReaderId:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value <= 0:
            raise InvalidValueObject("ID читателя должен быть целым числом > 0")


@dataclass(frozen=True)
class LoanId:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value <= 0:
            raise InvalidValueObject("ID выдачи должен быть целым числом > 0")


# ---------- Описательные значения ----------

@dataclass(frozen=True)
class CatalogNumber:
    """Каталожный номер книги, например «И-123»."""
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidValueObject("Каталожный номер не может быть пустым")


@dataclass(frozen=True)
class FullName:
    """ФИО читателя: минимум фамилия и имя."""
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or len(self.value.split()) < 2:
            raise InvalidValueObject("ФИО должно содержать хотя бы фамилию и имя")


@dataclass(frozen=True)
class Money:
    """Денежная сумма в рублях. Инвариант 5: сумма не может быть отрицательной."""
    amount: Decimal
    currency: str = "RUB"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise InvalidValueObject("Сумма должна быть Decimal")
        if self.amount < 0:
            raise InvalidValueObject("Сумма не может быть отрицательной")
        if self.currency != "RUB":
            raise InvalidValueObject("Поддерживаются только рубли")

    @staticmethod
    def zero() -> "Money":
        return Money(Decimal("0"))

    def __str__(self) -> str:
        return f"{self.amount} руб."


# Штраф за просрочку — всегда фиксированный, 1000 рублей
LATE_RETURN_FINE = Money(Decimal("1000"))


@dataclass(frozen=True)
class LoanPeriod:
    """Срок выдачи: дата выдачи и дата, до которой книгу нужно вернуть.

    Инвариант 6: срок возврата не может быть раньше даты выдачи.
    """
    issue_date: date
    due_date: date

    def __post_init__(self) -> None:
        if not isinstance(self.issue_date, date) or not isinstance(self.due_date, date):
            raise InvalidValueObject("Даты выдачи и возврата должны быть датами")
        if self.due_date < self.issue_date:
            raise InvalidValueObject("Срок возврата не может быть раньше даты выдачи")

    @staticmethod
    def starting(issue_date: date, days: int) -> "LoanPeriod":
        """Создаёт срок длительностью days дней от даты выдачи."""
        if not isinstance(days, int) or days <= 0:
            raise InvalidValueObject("Длительность выдачи должна быть > 0 дней")
        return LoanPeriod(issue_date, issue_date + timedelta(days=days))

    def is_overdue_on(self, return_date: date) -> bool:
        """Просрочен ли возврат в указанную дату."""
        return return_date > self.due_date

    def __str__(self) -> str:
        # Формат даты, как в таблице преподавателя: DD.MM.YY
        return f"{self.issue_date:%d.%m.%y} – {self.due_date:%d.%m.%y}"
