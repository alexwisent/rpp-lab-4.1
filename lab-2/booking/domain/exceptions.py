"""Доменные исключения предметной области «Бронирование переговорных»."""


class DomainError(Exception):
    """Базовый класс всех доменных ошибок."""


class InvalidValueObject(DomainError):
    """Объект-значение создаётся с недопустимыми данными."""


class DomainInvariantViolation(DomainError):
    """Операция нарушает инвариант агрегата."""


class AggregateNotFound(DomainError):
    """Агрегат с таким идентификатором не найден в репозитории."""
