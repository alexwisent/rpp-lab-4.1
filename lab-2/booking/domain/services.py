"""Доменные сервисы бронирования.

Создание брони требует данных нескольких агрегатов:
- Room (вместимость, часы работы),
- других Booking этой комнаты (нет ли пересечения),
- Employee (существует ли сотрудник).
Поэтому операция вынесена в доменный сервис.
"""

from .aggregates import Booking
from .exceptions import DomainInvariantViolation
from .repositories import BookingRepository, EmployeeRepository, RoomRepository
from .value_objects import BookingId, EmployeeId, ParticipantsCount, RoomId, TimeSlot


class BookRoomService:
    """Забронировать переговорную."""

    def __init__(self, rooms: RoomRepository, employees: EmployeeRepository,
                 bookings: BookingRepository) -> None:
        self._rooms = rooms
        self._employees = employees
        self._bookings = bookings

    def book(self, room_id: RoomId, employee_id: EmployeeId,
             slot: TimeSlot, participants: ParticipantsCount) -> Booking:
        self._employees.get(employee_id)               # сотрудник должен существовать
        room = self._rooms.get(room_id)
        room.ensure_can_host(slot, participants)       # инварианты 1 и 3 — у комнаты

        # Инвариант 2: брони одной комнаты не пересекаются по времени
        for other in self._bookings.list_by_room(room_id):
            if other.conflicts_with(slot):
                raise DomainInvariantViolation(
                    f"Комната уже занята: пересечение с бронью №{other.id.value} ({other.slot})")

        booking = Booking(self._bookings.next_id(), room.id, employee_id, slot, participants)
        self._bookings.save(booking)
        return booking


class ChangeParticipantsService:
    """Изменить число участников: нужна вместимость комнаты (другой агрегат)."""

    def __init__(self, rooms: RoomRepository, bookings: BookingRepository) -> None:
        self._rooms = rooms
        self._bookings = bookings

    def change(self, booking_id: BookingId, new_count: ParticipantsCount) -> Booking:
        booking = self._bookings.get(booking_id)
        room = self._rooms.get(booking.room_id)        # загружаем комнату по ID
        booking.change_participants(new_count, room.capacity)
        self._bookings.save(booking)
        return booking
