# Workshop 3 – Parking App

This workshop contains the three working components of the Parking App:
- **auth-service** (Java/Spring Boot) – authentication and JWT issuance at `http://localhost:8080/api/auth`.
- **core-service** (Python/FastAPI) – parking business logic at `http://localhost:8000/api/core`.
- **web** (static HTML/CSS/JS) – dashboard that calls the two backends.

## Run locally (no Docker)
### Auth service (Java + MySQL)
1. From the project root run:
   ```bash
   cd Workshop-3/auth-service
   mvn spring-boot:run
   ```
2. Runtime database: MySQL with defaults from `src/main/resources/application.properties` (`parking_auth`, user `parking_user`, password `parking_pass`). Override with `SPRING_DATASOURCE_URL`, `SPRING_DATASOURCE_USERNAME`, and `SPRING_DATASOURCE_PASSWORD` as needed.
3. The service starts on port **8080**.

### Core service (Python + PostgreSQL)
1. From the project root run:
   ```bash
   cd Workshop-3/core-service
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```
2. Runtime database: PostgreSQL (default URL `postgresql+psycopg2://admon:admon@localhost:5432/parking`). Override with `DATABASE_URL`.
3. The service starts on port **8000**.

### Web frontend (static)
1. Serve the static files from `Workshop-3/web` using any HTTP server:
   ```bash
   cd Workshop-3/web
   python -m http.server 5500
   ```
2. Open `http://localhost:5500` (JS files expect auth on 8080 and core on 8000).

## Database configuration notes
- **Auth service:** Production profile expects MySQL as above. The `test` profile uses an in-memory H2 database configured in `src/test/resources/application-test.properties` so unit tests do not require MySQL.
- **Core service:** Production defaults to PostgreSQL through `DATABASE_URL`. Pytest overrides the URL to SQLite to keep tests self-contained and seeds default slots on startup.

## REST API reference
### Auth service
- `POST /api/auth/register`
  - Request: `{ "username": "alice", "email": "alice@example.com", "password": "secret" }`
  - Response: `{ "access_token": "<jwt>", "user": { "id": 1, "username": "alice", "email": "alice@example.com" } }`
- `POST /api/auth/login`
  - Request: `{ "email": "alice@example.com", "password": "secret" }`
  - Response: same structure as register with a fresh JWT token.

### Core service
- `GET /api/core/stats/overview` → `{ "occupied": 0, "free": 25, "activeVehicles": 0, "occupancyPercent": 0.0, "currentRatePerMinute": 30, ... }`
- `GET /api/core/slots` → list of `{ "code": "A01", "occupied": false, "plate": null }`.
- `GET /api/core/sessions?limit=5&order=desc` → list with session timestamps, plate, slot code, and amount (when closed).
- `POST /api/core/entries` with `{ "plate": "ABC-123" }` → assigns a slot and returns `{ "plate": "ABC-123", "slot_code": "A01", "check_in_at": "..." }`.
- `POST /api/core/exits` with `{ "plate": "ABC-123" }` → closes the active session and returns receipt fields `{ "minutes": 5, "amount": 150, "currency": "COP", ... }`.

## Frontend integration
- JavaScript clients in `Workshop-3/web/js/api.js` and `Workshop-3/web/js/app.js` call the auth endpoints for **login** and **register** and the core endpoints for **overview stats**, **slots**, **sessions**, **entries**, and **exits**.
- The dashboard cards consume `/api/core/stats/overview`, slot lists are rendered from `/api/core/slots`, and vehicle actions use `/api/core/entries` and `/api/core/exits` while keeping the login JWT from `/api/auth/login` in `localStorage`.

## Running unit tests
- Java (from `Workshop-3/auth-service`):
  ```bash
  mvn test
  ```
- Python (from `Workshop-3/core-service`):
  ```bash
  pytest -q
  ```
