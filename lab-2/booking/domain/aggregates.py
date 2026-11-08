"""Агрегаты бронирования: Room, Booking, Employee.

Состояние — в закрытых полях, снаружи только чтение через @property.
Изменения — только через методы корня, которые проверяют инварианты.
"""

from enum import Enum

from .exceptions import DomainInvariantViolation
from .value_objects import (
    BookingId,
    Capacity,
    EmployeeId,
    FullName,
    OfficeHours,
    ParticipantsCount,
    RoomId,
    RoomName,
    TimeSlot,
)


class Room:
    """Корень агрегата «Комната»: вместимость и часы работы офиса.

    Комната сама проверяет, может ли она принять встречу:
    инвариант 1 — участников не больше вместимости;
    инвариант 3 — бронь в пределах часов работы.
    """

    def __init__(self, room_id: RoomId, name: RoomName,
                 capacity: Capacity, office_hours: OfficeHours) -> None:
        self._id = room_id
        self._name = name
        self._capacity = capacity
        self._office_hours = office_hours

    @property
    def id(self) -> RoomId:
        return self._id

    @property
    def name(self) -> RoomName:
        return self._name

    @property
    def capacity(self) -> Capacity:
        return self._capacity

    @property
    def office_hours(self) -> OfficeHours:
        return self._office_hours

    def ensure_can_host(self, slot: TimeSlot, participants: ParticipantsCount) -> None:
        """Проверить, что встречу можно провести в этой комнате."""
        # Инвариант 1
        if participants.value > self._capacity.value:
            raise DomainInvariantViolation(
                f"В комнате «{self._name.value}» максимум {self._capacity.value} чел., "
                f"а участников {participants.value}")
        # Инвариант 3
        if not self._office_hours.covers(slot):
            raise DomainInvariantViolation(
                f"Бронь {slot} выходит за часы работы офиса {self._office_hours}")

    def __repr__(self) -> str:
        return (f"Room(id={self._id.value}, «{self._name.value}», "
                f"до {self._capacity.value} чел., {self._office_hours})")


class BookingStatus(Enum):
    ACTIVE = "Активна"
    CANCELLED = "Отменена"


class Booking:
    """Корень агрегата «Бронь».

    Хранит room_id и employee_id — только идентификаторы,
    а не объекты Room и Employee (связь по ID).

    Инварианты внутри брони:
    5 — отменённую бронь нельзя отменить повторно;
    6 — у отменённой брони нельзя менять число участников.
    """

    def __init__(self, booking_id: BookingId, room_id: RoomId, employee_id: EmployeeId,
                 slot: TimeSlot, participants: ParticipantsCount) -> None:
        self._id = booking_id
        self._room_id = room_id
        self._employee_id = employee_id
        self._slot = slot
        self._participants = participants
        self._status = BookingStatus.ACTIVE

    @property
    def id(self) -> BookingId:
        return self._id

    @property
    def room_id(self) -> RoomId:
        return self._room_id

    @property
    def employee_id(self) -> EmployeeId:
        return self._employee_id

    @property
    def slot(self) -> TimeSlot:
        return self._slot

    @property
    def participants(self) -> ParticipantsCount:
        return self._participants

    @property
    def status(self) -> BookingStatus:
        return self._status

    @property
    def is_active(self) -> bool:
        return self._status is BookingStatus.ACTIVE

    def conflicts_with(self, slot: TimeSlot) -> bool:
        """Мешает ли эта бронь новой брони на интервал slot.

        Отменённая бронь комнату не занимает.
        """
        return self.is_active and self._slot.overlaps(slot)

    def cancel(self) -> None:
        # Инвариант 5
        if self._status is BookingStatus.CANCELLED:
            raise DomainInvariantViolation("Бронь уже отменена")
        self._status = BookingStatus.CANCELLED

    def change_participants(self, new_count: ParticipantsCount, room_capacity: Capacity) -> None:
        """Изменить число участников.

        Вместимость комнаты передаётся как значение (Capacity), а не объект Room —
        бронь не получает доступа к чужому агрегату.
        """
        # Инвариант 6
        if not self.is_active:
            raise DomainInvariantViolation("Нельзя изменить отменённую бронь")
        # Инвариант 1 при изменении
        if new_count.value > room_capacity.value:
            raise DomainInvariantViolation(
                f"Участников {new_count.value}, а вместимость {room_capacity.value}")
        self._participants = new_count

    def __repr__(self) -> str:
        return (f"Booking(id={self._id.value}, комната={self._room_id.value}, "
                f"сотрудник={self._employee_id.value}, {self._slot}, "
                f"{self._participants.value} чел., {self._status.value})")


class Employee:
    """Корень агрегата «Сотрудник». Простой агрегат: ID + ФИО."""

    def __init__(self, employee_id: EmployeeId, full_name: FullName) -> None:
        self._id = employee_id
        self._full_name = full_name

    @property
    def id(self) -> EmployeeId:
        return self._id

    @property
    def full_name(self) -> FullName:
        return self._full_name

    def __repr__(self) -> str:
        return f"Employee(id={self._id.value}, {self._full_name.value})"
