# CRM Telegram Bot

Telegram-бот для управления клиентами и продажами. Поддержка команд, работа в команде, воронка продаж, статистика и напоминания — всё через удобный inline-интерфейс.

## Возможности

- **Управление клиентами** — создание, редактирование, удаление, смена статуса. Многошаговая форма с возможностью пропуска необязательных полей (`/skip`).
- **Воронка продаж** — визуальная сводка по статусам (New → In Progress → Proposal Sent → Won / Lost) с drill-down в список клиентов.
- **Команды** — создание команды с инвайт-кодом, вступление, выход, управление участниками. Роли: Solo, Owner, Manager.
- **Статистика** — личная статистика (всего клиентов, выигранных, проигранных, выручка, конверсия) и командный лидерборд.
- **Напоминания** — установка даты и времени напоминания для клиента. Фоновая задача проверяет каждые 60 секунд и отправляет уведомление.
- **Мультиязычность** — полная поддержка русского и английского языков. Переключение в настройках.
- **Автоматическая регистрация** — новые пользователи регистрируются при первом взаимодействии.
- **Контроль доступа** — менеджеры видят только своих клиентов, владельцы команд — всех в команде.

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| Бот-фреймворк | [aiogram 3.15](https://docs.aiogram.dev/) |
| База данных | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Миграции | Alembic |
| FSM-хранилище | Redis 7 |
| Конфигурация | pydantic-settings |
| Контейнеризация | Docker / Docker Compose |
| Python | 3.11+ |

## Структура проекта

```
app/
├── __main__.py              # Точка входа
├── core/
│   ├── settings.py          # Конфигурация (Pydantic BaseSettings)
│   ├── enums.py             # UserRole, ClientStatus
│   ├── logging.py           # Настройка логирования
│   └── redis.py             # Подключение к Redis
├── db/
│   ├── base.py              # Декларативная база (created_at, updated_at)
│   ├── session.py           # Engine и session factory
│   ├── models/              # SQLAlchemy-модели (User, Team, Client)
│   └── repositories/        # Паттерн Repository для каждой модели
├── services/
│   ├── client.py            # Бизнес-логика клиентов и воронки
│   ├── team.py              # Создание/вступление/выход из команды
│   ├── stats.py             # Статистика и лидерборд
│   └── reminder.py          # Фоновый цикл напоминаний
└── bot/
    ├── factory.py           # Создание Bot и Dispatcher
    ├── error_handler.py     # Глобальный обработчик ошибок
    ├── handlers/            # Обработчики команд и callback-ов
    ├── keyboards/           # Inline-клавиатуры
    ├── lexicon/             # Тексты (ru.py, en.py)
    ├── middlewares/          # Database, Auth, I18n
    ├── filters/             # RoleFilter, TeamRequiredFilter
    ├── states/              # FSM-состояния
    └── utils/               # Пагинация
```

## Быстрый старт

### Требования

- Docker и Docker Compose
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

### 1. Клонирование

```bash
git clone https://github.com/arturA34/crm-telegram-bot.git
cd crm-telegram-bot
```

### 2. Настройка окружения

```bash
cp .env.example .env
```

Откройте `.env` и укажите свой токен бота:

```env
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

Остальные параметры можно оставить по умолчанию для локальной разработки.

### 3. Запуск

```bash
docker compose up -d
```

Это поднимет три контейнера:
- **bot** — приложение (автоматически применит миграции при старте)
- **postgres** — база данных
- **redis** — хранилище FSM-состояний

### 4. Проверка

```bash
docker compose logs -f bot
```

Бот готов к работе, когда в логах появится `Bot is starting polling`.

## Локальная разработка (без Docker)

### Требования

- Python 3.11+
- Запущенные PostgreSQL и Redis

### Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### Применение миграций

```bash
alembic upgrade head
```

### Запуск

```bash
python -m app
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `BOT_TOKEN` | Токен Telegram-бота | — (обязательно) |
| `POSTGRES_HOST` | Хост PostgreSQL | `postgres` |
| `POSTGRES_PORT` | Порт PostgreSQL | `5432` |
| `POSTGRES_USER` | Пользователь БД | `crm_bot` |
| `POSTGRES_PASSWORD` | Пароль БД | `crm_bot_secret` |
| `POSTGRES_DB` | Имя базы данных | `crm_bot` |
| `REDIS_HOST` | Хост Redis | `redis` |
| `REDIS_PORT` | Порт Redis | `6379` |
| `REDIS_DB` | Номер базы Redis | `0` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `DEBUG` | Режим отладки (echo SQL) | `false` |

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню |
| `/stats` | Личная статистика |
| `/leaderboard` | Командный лидерборд |
| `/skip` | Пропуск необязательного поля при создании клиента |

## Архитектура

Бот построен по слоистой архитектуре:

```
Handlers → Services → Repositories → SQLAlchemy Models → PostgreSQL
```

**Middleware-цепочка** (применяется к каждому входящему сообщению и callback):
1. `DatabaseMiddleware` — открывает async-сессию, коммитит при успехе, откатывает при ошибке
2. `AutoRegisterMiddleware` — автоматически создаёт пользователя при первом обращении
3. `I18nMiddleware` — подставляет словарь текстов по языку пользователя

**FSM** хранится в Redis. Используется для многошаговых форм: создание клиента (4 шага), редактирование клиента, установка напоминания (2 шага), создание/вступление в команду.
