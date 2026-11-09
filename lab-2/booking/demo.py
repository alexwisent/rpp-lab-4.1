"""Демонстрация доменной модели «Бронирование переговорных».

Запуск из папки lab-2:  python -m booking.demo
"""

from datetime import datetime, time

from booking.adapters.memory import (
    InMemoryBookingRepository,
    InMemoryEmployeeRepository,
    InMemoryRoomRepository,
)
from booking.domain.aggregates import Employee, Room
from booking.domain.exceptions import DomainError
from booking.domain.services import BookRoomService, ChangeParticipantsService
from booking.domain.value_objects import (
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


def try_action(title, action):
    """Выполнить действие и показать результат или доменную ошибку."""
    try:
        result = action()
        print(f"  [OK]     {title}: {result}")
    except DomainError as error:
        print(f"  [ОТКАЗ]  {title}: {type(error).__name__}: {error}")


def slot(day: int, start: str, end: str) -> TimeSlot:
    """Короткая запись интервала: slot(10, "10:00", "11:00") -> 10.11.26 10:00–11:00."""
    sh, sm = map(int, start.split(":"))
    eh, em = map(int, end.split(":"))
    return TimeSlot(datetime(2026, 11, day, sh, sm), datetime(2026, 11, day, eh, em))


def main() -> None:
    rooms = InMemoryRoomRepository()
    employees = InMemoryEmployeeRepository()
    bookings = InMemoryBookingRepository()

    book_room = BookRoomService(rooms, employees, bookings)
    change_participants = ChangeParticipantsService(rooms, bookings)

    room = Room(RoomId(1), RoomName("Байкал"), Capacity(6), OfficeHours(time(9, 0), time(18, 0)))
    rooms.save(room)
    employees.save(Employee(EmployeeId(1), FullName("Смирнова Ольга")))
    employees.save(Employee(EmployeeId(2), FullName("Кузнецов Павел")))

    print("=== Бронирование переговорных ===")
    print("Комната:", room)

    print("\n1. Обычная бронь")
    try_action("Смирнова бронирует 10:00–11:00 на 4 чел.",
               lambda: book_room.book(RoomId(1), EmployeeId(1), slot(10, "10:00", "11:00"),
                                      ParticipantsCount(4)))

    print("\n2. Инвариант 1: участников больше вместимости")
    try_action("Кузнецов бронирует 12:00–13:00 на 10 чел.",
               lambda: book_room.book(RoomId(1), EmployeeId(2), slot(10, "12:00", "13:00"),
                                      ParticipantsCount(10)))

    print("\n3. Инвариант 2: пересечение с другой бронью")
    try_action("Кузнецов бронирует 10:30–11:30",
               lambda: book_room.book(RoomId(1), EmployeeId(2), slot(10, "10:30", "11:30"),
                                      ParticipantsCount(3)))
    try_action("Кузнецов бронирует 11:00–12:00 (встык — можно)",
               lambda: book_room.book(RoomId(1), EmployeeId(2), slot(10, "11:00", "12:00"),
                                      ParticipantsCount(3)))

    print("\n4. Инвариант 3: вне часов работы офиса")
    try_action("Бронь 08:00–09:30",
               lambda: book_room.book(RoomId(1), EmployeeId(1), slot(10, "8:00", "9:30"),
                                      ParticipantsCount(2)))
    try_action("Бронь 17:30–19:00",
               lambda: book_room.book(RoomId(1), EmployeeId(1), slot(10, "17:30", "19:00"),
                                      ParticipantsCount(2)))

    print("\n5. Инвариант 4: начало позже окончания (объект-значение TimeSlot)")
    try_action("Интервал 15:00–14:00", lambda: slot(10, "15:00", "14:00"))

    print("\n6. Инвариант 5: повторная отмена")
    first = bookings.get(BookingId(1))
    try_action("Отменить бронь №1", lambda: (first.cancel(), first)[1])
    try_action("Отменить бронь №1 ещё раз", lambda: first.cancel())
    try_action("После отмены 10:00–11:00 снова свободно",
               lambda: book_room.book(RoomId(1), EmployeeId(2), slot(10, "10:00", "11:00"),
                                      ParticipantsCount(5)))

    print("\n7. Изменение числа участников (доменный сервис)")
    try_action("Бронь №2: стало 6 чел.",
               lambda: change_participants.change(BookingId(2), ParticipantsCount(6)))
    try_action("Бронь №2: стало 8 чел.",
               lambda: change_participants.change(BookingId(2), ParticipantsCount(8)))
    try_action("Инвариант 6: изменить отменённую бронь №1",
               lambda: change_participants.change(BookingId(1), ParticipantsCount(2)))

    print("\n8. Объекты-значения с плохими данными")
    try_action("Вместимость 0", lambda: Capacity(0))
    try_action("Участников -3", lambda: ParticipantsCount(-3))
    try_action("Офис 18:00–09:00", lambda: OfficeHours(time(18, 0), time(9, 0)))

    print("\nВсе брони комнаты «Байкал»:")
    for booking in bookings.all():
        print("  ", booking)


if __name__ == "__main__":
    main()
