# Python Core Service

FastAPI application that powers the parking domain (entries, exits, slots, billing) consumed by the Workshop-3 Web UI.

## Features

- FastAPI + SQLModel architecture with clear separation between API, services, and database helpers.
- Automatic schema creation and seeding on startup (`SYSTEM` operator, default fee, slots `A01`-`A04`).
- JWT-ready via dependency overrides; the Web UI forwards the token issued by the Java service.
- REST contract aligned with the frontend:
  - `GET /api/core/stats/overview`
  - `GET /api/core/sessions`
  - `GET /api/core/slots`
  - `POST /api/core/entries`
  - `POST /api/core/exits`
- Management endpoints under `/api/core/*` to CRUD users, fees, slots, tickets, and payments.
- Pytest suite with dependency overrides and in-memory SQLite database.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Environment variables (optional overrides):

```bash
export CORE_DATABASE_URL=postgresql://admon:admon@localhost:5432/parking
export SQL_DEBUG=true
```

Or configure granular keys instead:

```bash
export CORE_DB_HOST=localhost
export CORE_DB_PORT=5432
export CORE_DB_USER=admon
export CORE_DB_PASSWORD=admon
export CORE_DB_NAME=parking
```

## Testing

```bash
pytest
```

The suite spins up an in-memory SQLite engine, seeds baseline data, and exercises the entry/exit workflow plus session listings.
