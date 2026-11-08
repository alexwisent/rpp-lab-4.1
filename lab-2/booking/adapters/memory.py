"""In-memory реализации репозиториев бронирования (адаптеры)."""

from booking.domain.aggregates import Booking, Employee, Room
from booking.domain.exceptions import AggregateNotFound
from booking.domain.value_objects import BookingId, EmployeeId, RoomId


class InMemoryRoomRepository:
    def __init__(self) -> None:
        self._items: dict[RoomId, Room] = {}

    def get(self, room_id: RoomId) -> Room:
        if room_id not in self._items:
            raise AggregateNotFound(f"Комната {room_id.value} не найдена")
        return self._items[room_id]

    def save(self, room: Room) -> None:
        self._items[room.id] = room


class InMemoryEmployeeRepository:
    def __init__(self) -> None:
        self._items: dict[EmployeeId, Employee] = {}

    def get(self, employee_id: EmployeeId) -> Employee:
        if employee_id not in self._items:
            raise AggregateNotFound(f"Сотрудник {employee_id.value} не найден")
        return self._items[employee_id]

    def save(self, employee: Employee) -> None:
        self._items[employee.id] = employee


class InMemoryBookingRepository:
    def __init__(self) -> None:
        self._items: dict[BookingId, Booking] = {}
        self._last_id = 0

    def next_id(self) -> BookingId:
        self._last_id += 1
        return BookingId(self._last_id)

    def get(self, booking_id: BookingId) -> Booking:
        if booking_id not in self._items:
            raise AggregateNotFound(f"Бронь {booking_id.value} не найдена")
        return self._items[booking_id]

    def save(self, booking: Booking) -> None:
        self._items[booking.id] = booking

    def list_by_room(self, room_id: RoomId) -> list[Booking]:
        return [b for b in self._items.values() if b.room_id == room_id]

    def all(self) -> list[Booking]:
        return list(self._items.values())
