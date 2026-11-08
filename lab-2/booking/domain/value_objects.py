"""Объекты-значения бронирования переговорных.

Неизменяемые (frozen=True), сравниваются по значению,
проверяют данные в __post_init__.
"""

from dataclasses import dataclass
from datetime import datetime, time

from .exceptions import InvalidValueObject


# ---------- Идентификаторы ----------

@dataclass(frozen=True)
class RoomId:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value <= 0:
            raise InvalidValueObject("ID комнаты должен быть целым числом > 0")


@dataclass(frozen=True)
class BookingId:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value <= 0:
            raise InvalidValueObject("ID брони должен быть целым числом > 0")


@dataclass(frozen=True)
class EmployeeId:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value <= 0:
            raise InvalidValueObject("ID сотрудника должен быть целым числом > 0")


# ---------- Описательные значения ----------

@dataclass(frozen=True)
class RoomName:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidValueObject("Название комнаты не может быть пустым")


@dataclass(frozen=True)
class FullName:
    """ФИО сотрудника: минимум фамилия и имя."""
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or len(self.value.split()) < 2:
            raise InvalidValueObject("ФИО должно содержать хотя бы фамилию и имя")


@dataclass(frozen=True)
class Capacity:
    """Вместимость комнаты — максимальное число участников, > 0."""
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value <= 0:
            raise InvalidValueObject("Вместимость комнаты должна быть > 0")


@dataclass(frozen=True)
class ParticipantsCount:
    """Число участников встречи, > 0."""
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value <= 0:
            raise InvalidValueObject("Число участников должно быть > 0")


@dataclass(frozen=True)
class OfficeHours:
    """Часы работы офиса, например 09:00–18:00. Открытие раньше закрытия."""
    opens_at: time
    closes_at: time

    def __post_init__(self) -> None:
        if not isinstance(self.opens_at, time) or not isinstance(self.closes_at, time):
            raise InvalidValueObject("Часы работы задаются временем")
        if self.opens_at >= self.closes_at:
            raise InvalidValueObject("Офис должен открываться раньше, чем закрывается")

    def covers(self, slot: "TimeSlot") -> bool:
        """Помещается ли интервал брони в часы работы."""
        return self.opens_at <= slot.start.time() and slot.end.time() <= self.closes_at

    def __str__(self) -> str:
        return f"{self.opens_at:%H:%M}–{self.closes_at:%H:%M}"


@dataclass(frozen=True)
class TimeSlot:
    """Интервал брони [start, end).

    Начало строго раньше окончания, и бронь в пределах одного дня.
    """
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.start, datetime) or not isinstance(self.end, datetime):
            raise InvalidValueObject("Начало и окончание брони — дата и время")
        if self.start >= self.end:
            raise InvalidValueObject("Бронь не может закончиться раньше, чем начаться")
        if self.start.date() != self.end.date():
            raise InvalidValueObject("Бронь должна быть в пределах одного дня")

    def overlaps(self, other: "TimeSlot") -> bool:
        """Пересекаются ли интервалы. Встречи «встык» (10:00–11:00 и 11:00–12:00) не пересекаются."""
        return self.start < other.end and other.start < self.end

    def __str__(self) -> str:
        return f"{self.start:%d.%m.%y %H:%M}–{self.end:%H:%M}"
