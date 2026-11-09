"""Тесты доменной модели «Бронирование переговорных».

Запуск из папки lab-2:  python -m unittest -v
"""

import unittest
from datetime import datetime, time

from booking.adapters.memory import (
    InMemoryBookingRepository,
    InMemoryEmployeeRepository,
    InMemoryRoomRepository,
)
from booking.domain.aggregates import BookingStatus, Employee, Room
from booking.domain.exceptions import AggregateNotFound, DomainInvariantViolation, InvalidValueObject
from booking.domain.services import BookRoomService, ChangeParticipantsService
from booking.domain.value_objects import (
    Capacity,
    EmployeeId,
    FullName,
    OfficeHours,
    ParticipantsCount,
    RoomId,
    RoomName,
    TimeSlot,
)


def slot(start_h, end_h, day=10):
    return TimeSlot(datetime(2026, 11, day, start_h), datetime(2026, 11, day, end_h))


class BookingTestCase(unittest.TestCase):
    def setUp(self):
        self.rooms = InMemoryRoomRepository()
        self.employees = InMemoryEmployeeRepository()
        self.bookings = InMemoryBookingRepository()
        self.service = BookRoomService(self.rooms, self.employees, self.bookings)
        self.change = ChangeParticipantsService(self.rooms, self.bookings)

        self.rooms.save(Room(RoomId(1), RoomName("Байкал"), Capacity(6),
                             OfficeHours(time(9), time(18))))
        self.employees.save(Employee(EmployeeId(1), FullName("Смирнова Ольга")))

    def book(self, start_h, end_h, people=4):
        return self.service.book(RoomId(1), EmployeeId(1), slot(start_h, end_h),
                                 ParticipantsCount(people))

    def test_successful_booking(self):
        booking = self.book(10, 11)
        self.assertEqual(booking.status, BookingStatus.ACTIVE)
        self.assertEqual(booking.room_id, RoomId(1))   # связь по ID, а не объект

    # --- Инвариант 1 ---
    def test_participants_not_more_than_capacity(self):
        with self.assertRaises(DomainInvariantViolation):
            self.book(10, 11, people=7)

    # --- Инвариант 2 ---
    def test_overlapping_bookings_are_rejected(self):
        self.book(10, 12)
        with self.assertRaises(DomainInvariantViolation):
            self.book(11, 13)

    def test_back_to_back_bookings_are_allowed(self):
        self.book(10, 11)
        self.book(11, 12)                               # не должно бросить исключение
        self.assertEqual(len(self.bookings.all()), 2)

    def test_cancelled_booking_frees_the_room(self):
        first = self.book(10, 11)
        first.cancel()
        self.book(10, 11)

    # --- Инвариант 3 ---
    def test_booking_must_be_within_office_hours(self):
        with self.assertRaises(DomainInvariantViolation):
            self.book(8, 10)
        with self.assertRaises(DomainInvariantViolation):
            self.book(17, 19)

    # --- Инвариант 4 ---
    def test_slot_start_before_end(self):
        with self.assertRaises(InvalidValueObject):
            slot(12, 11)

    # --- Инвариант 5 ---
    def test_cannot_cancel_twice(self):
        booking = self.book(10, 11)
        booking.cancel()
        with self.assertRaises(DomainInvariantViolation):
            booking.cancel()

    # --- Инвариант 6 и изменение участников ---
    def test_change_participants_respects_capacity(self):
        booking = self.book(10, 11)
        self.change.change(booking.id, ParticipantsCount(6))
        self.assertEqual(booking.participants, ParticipantsCount(6))
        with self.assertRaises(DomainInvariantViolation):
            self.change.change(booking.id, ParticipantsCount(7))

    def test_cannot_change_cancelled_booking(self):
        booking = self.book(10, 11)
        booking.cancel()
        with self.assertRaises(DomainInvariantViolation):
            self.change.change(booking.id, ParticipantsCount(2))

    # --- Объекты-значения ---
    def test_value_objects_validate_input(self):
        for make in (lambda: Capacity(0), lambda: ParticipantsCount(-1),
                     lambda: OfficeHours(time(18), time(9)), lambda: RoomName("  ")):
            with self.assertRaises(InvalidValueObject):
                make()

    def test_unknown_employee(self):
        with self.assertRaises(AggregateNotFound):
            self.service.book(RoomId(1), EmployeeId(99), slot(10, 11), ParticipantsCount(2))

    def test_status_is_read_only(self):
        booking = self.book(10, 11)
        with self.assertRaises(AttributeError):
            booking.status = BookingStatus.CANCELLED


if __name__ == "__main__":
    unittest.main()
