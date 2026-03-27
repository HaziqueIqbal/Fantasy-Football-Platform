# Fantasy Football Platform — Backend API

A fully-featured Django REST API for a Fantasy Football Platform where users manage virtual teams, trade players on a transfer market, and track transaction history.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Model Relationships](#model-relationships)
- [API Endpoints](#api-endpoints)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Environment Setup](#environment-setup)
- [Running with Docker](#running-with-docker)
- [Running Locally (without Docker)](#running-locally-without-docker)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [Key Design Decisions](#key-design-decisions)

---

## Overview

This platform simulates a fantasy football league where:

- Each registered user automatically gets a team of **20 players** (3 GK, 5 DEF, 6 MID, 6 ATT) with an initial budget of **$5,000,000**.
- Every player starts at a value of **$1,000,000**.
- Users can list their players on the **Transfer Market** at any price.
- When a player is sold, their value **increases by a random 10–100%**.
- All completed transfers are recorded as immutable **Transactions**.
- Team capital and player values **cannot be changed directly** via the API.

---

## Architecture

The project follows the same layered architecture used in production Django services:

```
config/                    ← Project config (settings, urls, api_router)
fantasyfootball/           ← Application package
  common/                  ← Shared utilities (mixins, utils, auth, pagination, exceptions)
  user/                    ← Auth, registration, profile
  team/                    ← Team management + TeamService
  player/                  ← Player model + filtering
  transfer/                ← Transfer market (list, browse, buy)
  transaction/             ← Transaction history (read-only)
```

Each domain app contains:
- `models.py` — Django ORM models
- `admin.py` — Django admin registration
- `apps.py` — AppConfig (signals registered here)
- `filters.py` — django-filter FilterSets for search/filtering
- `signals.py` — Django signals (user app)
- `services.py` — Business logic layer (team app)
- `v1/` — Versioned API layer (serializers, views, urls)

---

## Model Relationships

```
User (1) ──────── (1) Team
                        │
                        │  (many)
                        ▼
                     Player ◄────── (many) TransferListing ◄──── (1) Transaction
                                                                         │
                                            User (seller) ──────────────►│
                                            User (buyer)  ──────────────►│
                                            Team (from)   ──────────────►│
                                            Team (to)     ──────────────►│
```

### Entity Descriptions

| Model | Key Fields | Notes |
|-------|------------|-------|
| **User** | `id` (UUID), `email` (unique), `first_name`, `last_name` | Custom user model; email is the login credential |
| **Team** | `id` (UUID), `name`, `owner` (FK→User), `budget` (Decimal) | One team per user; budget starts at $5,000,000 |
| **Player** | `id` (UUID), `first_name`, `last_name`, `position`, `value`, `team` (FK→Team) | Position: goalkeeper/defender/midfielder/attacker; value starts at $1,000,000 |
| **TransferListing** | `id` (UUID), `player` (FK→Player), `seller` (FK→User), `asking_price`, `is_active` | `is_active=False` after sale or removal; a player may have multiple listings over time (one active at most) |
| **Transaction** | `id` (UUID), `player`, `from_team`, `to_team`, `seller`, `buyer`, `transfer_amount`, `transfer_listing` | Immutable record; `delete()` raises `NotImplementedError` |

### Constraints
- `Team.budget` and `Player.value` cannot be modified through the API directly
- A `TransferListing` is marked `is_active=False` after completion — never deleted
- A completed `Transaction` cannot be deleted (enforced at model level)

---

## API Endpoints

Base URL: `/api/`

### Authentication (`/api/user/v1/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/user/v1/register/` | Register a new user (creates team + 20 players automatically) | No |
| `POST` | `/api/user/v1/login/` | Login with email + password → returns JWT tokens | No |
| `POST` | `/api/user/v1/logout/` | Blacklist the refresh token | Yes |
| `POST` | `/api/user/v1/token/refresh/` | Refresh the access token | No |
| `GET` | `/api/user/v1/profile/` | Get current user's profile | Yes |
| `PUT` | `/api/user/v1/profile/` | Update current user's profile | Yes |

### Teams (`/api/team/v1/teams/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/team/v1/teams/` | List all teams (paginated, searchable) | Yes |
| `GET` | `/api/team/v1/teams/my/` | Get current user's team with all players | Yes |
| `GET` | `/api/team/v1/teams/<uuid>/` | Get a specific team by ID | Yes |

**Query params:** `search`, `ordering`, `page`, `page_size`

### Players (`/api/player/v1/players/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/player/v1/players/` | List all players (paginated, filterable) | Yes |
| `GET` | `/api/player/v1/players/<uuid>/` | Get a specific player | Yes |

**Filters:** `position`, `country`, `team`, `min_value`, `max_value`, `first_name`, `last_name`
**Search:** `first_name`, `last_name`, `country`
**Ordering:** `value`, `position`, `last_name`, `created_at`

### Transfer Market (`/api/transfer/v1/transfer/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/transfer/v1/transfer/` | Browse all active transfer listings | Yes |
| `POST` | `/api/transfer/v1/transfer/list/` | List a player for sale | Yes |
| `DELETE` | `/api/transfer/v1/transfer/<uuid>/` | Remove your listing (sets is_active=False) | Yes |
| `POST` | `/api/transfer/v1/transfer/<uuid>/buy/` | Buy a listed player | Yes |

**Filters (market):** `position`, `player_name`, `country`, `min_price`, `max_price`
**Ordering:** `asking_price`, `created_at`

### Transaction History (`/api/transaction/v1/transactions/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/transaction/v1/transactions/` | List all completed transfers | Yes |
| `GET` | `/api/transaction/v1/transactions/<uuid>/` | Get transaction details | Yes |

**Filters:** `buyer`, `seller`, `from_team`, `to_team`, `min_amount`, `max_amount`
**Ordering:** `transfer_amount`, `created_at`

---

## Tech Stack

| Component | Library/Version |
|-----------|----------------|
| Framework | Django 6.0.3 |
| REST API | Django REST Framework 3.17.1 |
| Authentication | SimpleJWT 5.5.1 (HS256, cookie + Bearer header) |
| Filtering | django-filter 25.2 |
| API Schema | drf-spectacular 0.29.0 (OpenAPI 3) |
| Database | PostgreSQL 15 (via Docker) |
| Environment | django-environ 0.13.0 |
| Static Files | WhiteNoise 6.12.0 |
| Testing | pytest + pytest-django + pytest-cov |
| Containerisation | Docker + Docker Compose |

---

## Project Structure

```
Fantasy Football Platform/
├── config/                           # Django project config
│   ├── settings/
│   │   ├── base.py                   # Shared settings
│   │   ├── local.py                  # Development settings (active)
│   │   └── test.py                   # Test settings (in-memory SQLite)
│   ├── api_router.py                 # Central URL router
│   ├── urls.py                       # Root URL config + Swagger
│   ├── wsgi.py
│   └── asgi.py
│
├── fantasyfootball/                  # Application package
│   ├── common/                       # Shared components
│   │   ├── authentication.py         # Cookie/Bearer JWT authentication
│   │   ├── exception_handler.py      # Unified error envelope
│   │   ├── exceptions.py             # Custom DRF exceptions
│   │   ├── mixins.py                 # UUIDMixin, AuditMixin, BaseModel
│   │   ├── pagination.py             # StandardResultsPagination
│   │   └── utils.py                  # format_response()
│   │
│   ├── user/                         # User management
│   │   ├── models.py                 # Custom User (email login, UUID PK)
│   │   ├── signals.py                # post_save → create team + 20 players
│   │   └── v1/
│   │       ├── serializers.py
│   │       ├── views.py              # Register, Login, Logout, Profile
│   │       └── urls.py
│   │
│   ├── team/                         # Team management
│   │   ├── models.py                 # Team (budget, owner, total_value property)
│   │   ├── services.py               # TeamService.create_team_for_user()
│   │   └── v1/
│   │       ├── serializers.py
│   │       ├── views.py              # MyTeam, TeamList, TeamDetail
│   │       └── urls.py
│   │
│   ├── player/                       # Player management
│   │   ├── models.py                 # Player (position, value, team FK)
│   │   ├── filters.py                # PlayerFilter (position, country, value range)
│   │   └── v1/
│   │       ├── serializers.py
│   │       ├── views.py              # PlayerList, PlayerDetail
│   │       └── urls.py
│   │
│   ├── transfer/                     # Transfer market
│   │   ├── models.py                 # TransferListing (player, seller, asking_price, is_active)
│   │   ├── filters.py                # TransferListingFilter
│   │   └── v1/
│   │       ├── serializers.py
│   │       ├── views.py              # Market, ListForSale, Detail, BuyPlayer
│   │       └── urls.py
│   │
│   └── transaction/                  # Transaction history
│       ├── models.py                 # Transaction (immutable, delete() raises NotImplementedError)
│       ├── filters.py                # TransactionFilter
│       └── v1/
│           ├── serializers.py
│           ├── views.py              # TransactionList, TransactionDetail
│           └── urls.py
│
├── tests/                            # Test suite
│   ├── conftest.py                   # Shared fixtures (users, teams, players, listings)
│   ├── test_user.py                  # Registration, login, profile tests
│   ├── test_team.py                  # Team creation, player distribution, API tests
│   ├── test_player.py                # Player listing, filtering, search tests
│   ├── test_transfer.py              # Transfer market, buy player, constraints tests
│   └── test_transaction.py          # Transaction history, immutability tests
│
├── compose/
│   └── local/django/
│       ├── Dockerfile                # Local dev image (Python 3.12-slim)
│       └── start                    # migrate + collectstatic + runserver
│
├── requirements/
│   ├── base.txt                      # Core dependencies
│   └── local.txt                     # Dev + test dependencies
│
├── Dockerfile                        # Standalone local image (manual docker run)
├── docker-compose.yml                # Local dev stack (Django + PostgreSQL)
├── manage.py
├── pytest.ini                        # pytest + coverage config
├── .env.example                      # Environment variable template
├── .gitignore
└── .dockerignore
```

---

## Environment Setup

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Key variables:

| Variable | Example Value | Description |
|----------|---------------|-------------|
| `SECRET_KEY` | `your-strong-secret-key` | Django secret key — generate one with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `True` | Enable debug mode |
| `DATABASE_URL` | `postgres://postgres:postgres@localhost:5432/fantasyfootball` | PostgreSQL connection string |
| `ALLOWED_HOSTS` | `localhost,0.0.0.0,127.0.0.1,backend` | Comma-separated allowed hosts |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | `60` | JWT access token lifetime |
| `REFRESH_TOKEN_LIFETIME_DAYS` | `7` | JWT refresh token lifetime |
| `DEFAULT_PAGE_LIMIT` | `15` | Default pagination page size |
| `TRANSFER_VALUE_INCREASE_MIN` | `10` | Minimum % increase on player value after transfer |
| `TRANSFER_VALUE_INCREASE_MAX` | `100` | Maximum % increase on player value after transfer |

---

## Running with Docker

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/install/) ≥ 2

### 1. Set up environment

```bash
cp .env.example .env
# Edit .env if needed — defaults work out of the box with Docker
```

### 2. Build and start

```bash
docker compose up --build
```

This starts two services:
- **db** — PostgreSQL 15 on port `5432`
- **backend** — Django dev server on port `8000`

Migrations run automatically on startup. The API is available at **http://localhost:8000**.

> **How the DB connection works inside Docker:**
> The `backend` service overrides `DATABASE_URL` to `postgres://postgres:postgres@db:5432/fantasyfootball` — using the Docker Compose service hostname `db` instead of `localhost`. Your `.env` keeps `localhost` for running outside Docker.

### 3. Useful commands

```bash
# Run in background
docker compose up --build -d

# View live logs
docker compose logs -f backend

# Open a Django shell
docker compose exec backend python manage.py shell

# Create a superuser
docker compose exec backend python manage.py createsuperuser

# Run tests inside the container
docker compose exec backend python -m pytest tests/ -v

# Stop services
docker compose down

# Stop and wipe the database volume
docker compose down -v
```

---

## Running Locally (without Docker)

### Prerequisites
- Python 3.12+
- A running PostgreSQL instance (update `DATABASE_URL` in `.env` accordingly)

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements/local.txt

# Apply migrations
python manage.py migrate

# (Optional) Create a superuser for Django Admin
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The API is available at **http://localhost:8000**.

---

## Running Tests

Tests use an **in-memory SQLite database** (`config.settings.test`) so no running Postgres is needed.

```bash
# Activate the virtual environment first
source .venv/bin/activate

# Run all tests with coverage report
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_user.py -v

# Run a specific test class
python -m pytest tests/test_transfer.py::TestBuyPlayer -v

# Generate HTML coverage report
python -m pytest tests/ --cov=fantasyfootball --cov-report=html
# Then open htmlcov/index.html in your browser
```

**Or run tests inside the Docker container:**

```bash
docker compose exec backend python -m pytest tests/ -v
```

Current test stats: **46 tests | 92.87% coverage**.

### Test categories

| File | What it covers |
|------|----------------|
| `test_user.py` | Registration, login, profile, auth required |
| `test_team.py` | Auto-team creation, player distribution, API endpoints |
| `test_player.py` | Listing, filtering by position/country, search, pagination |
| `test_transfer.py` | List for sale, browse market, buy player, budget enforcement, constraints |
| `test_transaction.py` | History listing, filters, immutability, auth required |

---

## API Documentation

Interactive API docs are auto-generated via **drf-spectacular**:

| URL | Description |
|-----|-------------|
| `http://localhost:8000/api/docs/` | Swagger UI |
| `http://localhost:8000/api/redoc/` | ReDoc |
| `http://localhost:8000/api/schema/` | Raw OpenAPI 3 schema |

Django Admin is available at `http://localhost:8000/admin/`.

---

## Key Design Decisions

### Authentication
- **JWT (SimpleJWT, HS256)** with access + refresh token rotation.
- Tokens are accepted via the `Authorization: Bearer <token>` header **or** an `access` cookie (cookie-based auth common in browser apps).
- Refresh tokens are **rotated on every `/token/refresh/` call** — the old token is blacklisted and a new one is issued.
- Refresh tokens are **blacklisted on logout** to prevent reuse.

### Signals
- A `post_save` signal on `User` fires `TeamService.create_team_for_user()` immediately after a user is registered, ensuring every user always has a team with 20 players.

### Transfer Business Logic
The entire buy-player flow in `BuyPlayerView.post()` is wrapped in `@transaction.atomic` to guarantee:
1. Buyer budget deducted.
2. Seller budget credited.
3. Player team changed.
4. Player value increased by random 10–100%.
5. `TransferListing.is_active` set to `False`.
6. `Transaction` record created.

All 6 steps happen atomically — no partial updates.

### Immutability Constraints
- `Transaction.delete()` raises `NotImplementedError` at the model level.
- The Django Admin has `has_delete_permission = False` for transactions.
- `TransferListing` is never physically deleted; `is_active` is set to `False`.

### Performance Optimizations
- `select_related` / `prefetch_related` on all list views to avoid N+1 queries.
- Database indexes on frequently filtered fields: `position`, `team`, `value`, `is_active`, `buyer/seller`.
- `bulk_create` in `TeamService` to create all 20 players in a single SQL statement.
- `PageNumberPagination` with configurable `page_size` (default 15, max 100).

### Response Envelope
Every API response follows a consistent structure:

```json
{
  "status_code": 200,
  "message": "message",
  "data": { ... },
  "success": true
}
```

Errors follow the same shape with `"success": false`.
