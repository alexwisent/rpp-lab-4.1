# Лабораторная работа №2. Проектирование доменной модели с помощью DDD

Две предметные области:

1. **Библиотека** (вариант 1 из методички) — `library/`
2. **Бронирование переговорных комнат** (вариант 3 из методички) — `booking/`

## Структура

```
lab-2/
├── library/                 # Предметная область 1. Библиотека
│   ├── domain/              # доменный слой — только «чистый» Python
│   │   ├── exceptions.py    # иерархия доменных исключений
│   │   ├── value_objects.py # объекты-значения (frozen dataclass + __post_init__)
│   │   ├── aggregates.py    # агрегаты Book, Loan, Reader
│   │   ├── repositories.py  # порты репозиториев (Protocol)
│   │   └── services.py      # доменные сервисы CheckoutService, ReturnService
│   ├── adapters/
│   │   └── memory.py        # in-memory репозитории (словари)
│   └── demo.py              # демонстрация всех инвариантов
├── booking/                 # Предметная область 2. Бронирование переговорных
│   ├── domain/              # та же структура: Room, Booking, Employee
│   ├── adapters/memory.py
│   └── demo.py
└── tests/                   # тесты на unittest (ничего устанавливать не нужно)
```

## Запуск (из папки lab-2)

```bash
cd lab-2
python -m library.demo        # демонстрация «Библиотеки»
python -m booking.demo        # демонстрация «Бронирования»
python -m unittest -v         # все тесты
```

Штраф за просрочку возврата книги — всегда 1000 рублей.
