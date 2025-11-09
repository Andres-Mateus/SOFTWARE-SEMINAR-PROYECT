# Workshop 3 – Parking Platform Integration Guide

This workshop delivers a fully aligned tri-layer architecture ready for the Parking Web UI:

```
Workshop-3/
├── java-backend     # Spring Boot authentication & access-code service
├── python-backend   # Core parking logic service (FastAPI)
└── web-gui          # Static Web UI consuming both backends
```

The repository now includes updated REST routes, seed data, automated tests, and centralized documentation to support classroom demos or production deployments.

---

## 1. Quick start

### 1.1 Java authentication backend (`java-backend`)

| Item | Value |
| --- | --- |
| Port | `8080`
| Build tool | Maven 3.9+
| JDK | Temurin/OpenJDK 17
| Default DB | MySQL 8 (see §2)
| Swagger UI | `http://localhost:8080/swagger-ui/index.html`

```bash
cd Workshop-3/java-backend
./mvnw spring-boot:run
```

Environment variables (override defaults in `src/main/resources/application.properties`):

- `SPRING_DATASOURCE_URL` – e.g. `jdbc:mysql://localhost:3306/parking_db`
- `SPRING_DATASOURCE_USERNAME`
- `SPRING_DATASOURCE_PASSWORD`
- `APP_JWT_SECRET`

### 1.2 Python core backend (`python-backend`)

| Item | Value |
| --- | --- |
| Port | `8000`
| Runtime | Python 3.11+
| Framework | FastAPI + Uvicorn
| Default DB | PostgreSQL 15 (see §2) – falls back to SQLite for tests
| OpenAPI | `http://localhost:8000/docs`

```bash
cd Workshop-3/python-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Environment variables:

- `CORE_DATABASE_URL` – complete SQLAlchemy URL
- or granular overrides: `CORE_DB_DRIVER`, `CORE_DB_HOST`, `CORE_DB_PORT`, `CORE_DB_USER`, `CORE_DB_PASSWORD`, `CORE_DB_NAME`
- `SQL_DEBUG` – set to `true` to echo SQL statements

### 1.3 Web UI (`web-gui`)

The frontend is a framework-free SPA that expects both backends online.

```bash
cd Workshop-3/web-gui
python -m http.server 8081
```

Endpoints configured in `js/api.js`:

- `AUTH_API_URL = http://localhost:8080/api/auth`
- `CORE_API_URL = http://localhost:8000/api/core`

The Web UI automatically stores JWT tokens, adds the `Authorization` header, and shows live data from the core service once authenticated.

---

## 2. Database connectivity reference

| Service | Database | Default port | Driver | Secure credential tips | Schema notes |
| --- | --- | --- | --- | --- | --- |
| Java backend | MySQL 8 | `3306` | `com.mysql.cj.jdbc.Driver` (via `mysql-connector-java`) | Use dedicated MySQL user with least privileges, store secrets via Spring config server, Vault, or environment variables. | Tables: `user`, `role`, `access_code`. `DataInitializer` seeds admin user and first access code. |
| Python backend | PostgreSQL 15 | `5432` | `psycopg2` (SQLAlchemy URL `postgresql://...`) | Create read/write role with limited schema access, keep secrets in `.env` files loaded by `python-dotenv`. | Tables: `userp`, `vehicle`, `fee`, `ticket`, `payment`, `lotspace`. Startup seeding creates `SYSTEM` operator, default car fee, and demo slots `A01`-`A04`. |

To run the services locally without external servers you can also point `CORE_DATABASE_URL` to an SQLite database (`sqlite:///./parking.db`).

---

## 3. REST API catalogue

### 3.1 Java authentication service

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Creates a user using a single-use access code. |
| `POST` | `/api/auth/login` | Authenticates by e-mail and returns a JWT plus user profile. |
| `POST` | `/api/admin/access-code/generate` | (Admin only) issues a new 30-day access code. |

#### `POST /api/auth/register`

```jsonc
Request
{
  "email": "user@example.com",
  "password": "StrongPass#123",
  "accessCode": "REGISTER-2025-01",
  "username": "user" // optional – derived from email when missing
}
```

```jsonc
Response 200
{
  "message": "User created successfully"
}
```

#### `POST /api/auth/login`

```jsonc
Request
{
  "email": "user@example.com",
  "password": "StrongPass#123"
}
```

```jsonc
Response 200
{
  "accessToken": "<JWT>",
  "tokenType": "Bearer",
  "user": {
    "username": "user",
    "email": "user@example.com",
    "role": "ROLE_USER",
    "roles": ["ROLE_USER"]
  }
}
```

### 3.2 Python core service

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/core/stats/overview` | Aggregated KPIs for dashboard cards. |
| `GET` | `/api/core/sessions?limit=5&order=desc` | Recent parking sessions (ordered, limited). |
| `GET` | `/api/core/slots` | Current state of each parking slot. |
| `POST` | `/api/core/entries` | Registers a vehicle entry and allocates a slot. |
| `POST` | `/api/core/exits` | Closes the active ticket, frees the slot, and returns billing info. |
| `GET` | `/api/core/users` | Management endpoints (admin tooling). |
| `POST` | `/api/core/fees` | Management endpoints for pricing catalog. |
| `POST` | `/api/core/slots` | Allows provisioning of additional slots. |

#### `POST /api/core/entries`

```jsonc
Request
{
  "plate": "ABC123",
  "vehicle_type": "CAR",   // optional, defaults to CAR
  "owner_document": "DNI-778899", // optional – autogenerated when missing
  "fee_id": "FEE-CAR-HOURLY",    // optional – resolved by vehicle type
  "user_id": "SYSTEM"            // optional – system operator when missing
}
```

```jsonc
Response 201
{
  "session_id": 17,
  "plate": "ABC123",
  "slot_code": "A02",
  "check_in_at": "2025-05-22T19:05:12.514Z"
}
```

#### `POST /api/core/exits`

```jsonc
Request
{
  "plate": "ABC123"
}
```

```jsonc
Response 200
{
  "session_id": 17,
  "plate": "ABC123",
  "minutes": 95,
  "amount": 7600.0,
  "check_in_at": "2025-05-22T17:30:00Z",
  "check_out_at": "2025-05-22T19:05:00Z"
}
```

Slots endpoint example:

```jsonc
GET /api/core/slots
[
  { "code": "A01", "type": "CAR", "occupied": false, "plate": null },
  { "code": "A02", "type": "CAR", "occupied": true, "plate": "ABC123" }
]
```

---

## 4. Web UI integration contract

The SPA (`web-gui`) now mirrors the API contract described above:

- Login uses `/api/auth/login` and persists `accessToken` in `localStorage`.
- Registration posts to `/api/auth/register` with the camelCase payload expected by Spring Boot.
- Every protected call (entries, exits, stats, slots, sessions) automatically attaches `Authorization: Bearer <token>`.
- Vehicle workflow messages are driven by the JSON returned by `/api/core/entries` and `/api/core/exits` (slot code, minutes, amount).

CORS rules:

- Java backend allows origins `http://localhost:8081` and `http://127.0.0.1:8081`.
- Python backend exposes the same origins through `CORSMiddleware`.

---

## 5. Automated testing

| Service | Command | Notes |
| --- | --- | --- |
| Java backend | `mvn test` | Requires Maven to download Spring Boot dependencies (internet access needed). |
| Python backend | `pytest` | Uses FastAPI TestClient with in-memory SQLite via SQLModel. |

> **Offline environments**: Both toolchains download dependencies (Spring Boot starters, FastAPI, SQLModel). If your classroom or CI environment is air-gapped, configure an internal package proxy or preload the required wheels/jars before running these commands.

---

## 6. Evidence & observability

- JUnit suite validates JWT generation/validation logic (`JwtUtilTest`).
- Pytest suite exercises the entry/exit flow, slots availability, and session listings end-to-end.
- Screenshots or screencasts of the Web UI interacting with both services should be captured after executing:
  1. `uvicorn main:app --reload --port 8000`
  2. `./mvnw spring-boot:run`
  3. `python -m http.server 8081`

Happy parking! 🚗
