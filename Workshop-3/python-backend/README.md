# FastAPI core service

This service exposes the domain CRUD required by the parking management system. It uses SQLModel on top of PostgreSQL by default, but can operate with SQLite for development and automated testing.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlmodel psycopg2-binary python-dotenv pytest
uvicorn main:app --reload
```

The server listens on `http://localhost:8000` and serves interactive documentation at `/docs` and `/redoc`.

## Configuration

Set the following environment variables (or provide a single `DATABASE_URL`) before starting the app:

- `DATABASE_URL`: full SQLAlchemy URL (e.g. `postgresql://user:pass@localhost:5432/parking`).
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: fallback parameters to build the URL.
- User names, passwords and database names are percent-encoded automatically, so credentials with spaces or non-ASCII
  characters can be supplied without additional escaping.
- `SQL_ECHO`: set to `true` to print SQL statements for debugging.

`database.py` automatically detects SQLite URLs and enables the correct `check_same_thread` flag, allowing the in-memory database used by the test suite.

## Testing

```
pytest
```

The tests spin up an in-memory SQLite database, override the FastAPI dependency, and exercise `/api/core/users` end-to-end through the `TestClient`.

## Available endpoints

All routes are mounted under `/api/core`:

- `POST /users` and `GET /users`
- `GET /users/{id_user}` and `DELETE /users/{id_user}`
- `POST /vehicles` and `GET /vehicles`
- `POST /fees` and `GET /fees`
- `POST /tickets` and `GET /tickets`
- `POST /payments` and `GET /payments`
- `POST /lotspaces` and `GET /lotspaces`

Refer to `schemas.py` for the full payload definitions.
