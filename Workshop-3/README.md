# Workshop 3 – Parking App

This workspace contains the three parts required by the workshop:

- **auth-service** (Java/Spring Boot): authentication with MySQL and JWT under `http://localhost:8080/api/auth`.
- **core-service** (Python/FastAPI): business logic with PostgreSQL/SQLAlchemy under `http://localhost:8000/api/core`.
- **web** (static HTML/CSS/JS): frontend that calls the two backends.

## Running the services

### Auth service (Java + MySQL)
1. Set MySQL credentials in `auth-service/src/main/resources/application.properties` or export environment variables to override the datasource URL/user/password.
2. Install dependencies and start:
   ```bash
   cd Workshop-3/auth-service
   mvn spring-boot:run
   ```
3. Exposes `http://localhost:8080/api/auth`.

JUnit tests:
```bash
cd Workshop-3/auth-service
mvn test
```

### Core service (Python + PostgreSQL)
1. Configure a PostgreSQL connection string via `DATABASE_URL` (default: `postgresql+psycopg2://admon:admon@localhost:5432/parking`).
2. Install dependencies and start:
   ```bash
   cd Workshop-3/core-service
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. Exposes `http://localhost:8000/api/core`.

Pytest suite:
```bash
cd Workshop-3/core-service
pytest
```

### Frontend (static web)
1. From `Workshop-3/web`, serve the static files (any HTTP server works):
   ```bash
   cd Workshop-3/web
   python -m http.server 5500
   ```
2. Open `http://localhost:5500` (or your chosen port). The JS files call the auth service on port 8080 and the core service on port 8000.

## REST endpoints

### Auth service
- `POST /api/auth/register` – body `{ "username", "email", "password" }` → `{ "access_token", "user" }`.
- `POST /api/auth/login` – body `{ "email", "password" }` → `{ "access_token", "user" }`.

### Core service
- `GET /api/core/stats/overview` – dashboard KPIs (occupied/free/active/rate/percent).
- `GET /api/core/sessions?limit=&order=` – recent sessions for activity lists.
- `GET /api/core/slots` – slot occupancy with assigned plate if active.
- `POST /api/core/entries` – body `{ "plate" }` assigns a free slot and opens a session.
- `POST /api/core/exits` – body `{ "plate" }` closes the active session, returns minutes and amount.

## Frontend flows → backend mapping
- **Login** (form in `web/js/app.js`): `POST /api/auth/login` with email/password; stores `access_token` in `localStorage`.
- **Register**: `POST /api/auth/register` with username/email/password; success message then redirect to login.
- **Dashboard KPIs**: `GET /api/core/stats/overview` populates cards and occupancy bar.
- **Recent activity**: `GET /api/core/sessions` populates the dashboard and vehicles activity lists.
- **Slots view**: `GET /api/core/slots` renders slot status and active plate.
- **Vehicle entry**: `POST /api/core/entries` with `{plate}`; response shows assigned slot.
- **Vehicle exit**: `POST /api/core/exits` with `{plate}`; response shows minutes and total amount.

## Database notes
- The auth service expects a MySQL database named `parking_auth` by default.
- The core service uses PostgreSQL by default and seeds default slots (`A01`, `A02`, `A03`, `B01`, `B02`) on startup. Override `DATABASE_URL` to point to your database; SQLite is used automatically for the pytest suite.

## Ports
- Auth service: **8080**
- Core service: **8000**
- Frontend (example dev server): **5500**
