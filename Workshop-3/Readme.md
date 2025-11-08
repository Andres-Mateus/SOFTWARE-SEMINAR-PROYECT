# Workshop 3 – Parking Management System

This workspace implements the full stack requested for Workshop 3: a Java authentication service, a Python core service, and a static Web UI that consumes both REST APIs. The code base is organised and documented entirely in English and includes automated tests for both backends.

## Repository layout

```
Workshop-3/
├── java-backend/        # Spring Boot authentication API backed by MySQL
├── python-backend/      # FastAPI core domain API backed by PostgreSQL (or SQLite for tests)
├── web-gui/             # Static web console that consumes both APIs
├── docs/                # Architecture and integration notes
└── Readme.md            # This file
```

## Service overview

| Layer | Technology | Responsibilities |
| --- | --- | --- |
| Java backend | Spring Boot 3, Spring Security, JWT | User registration through single-use access codes, credential validation, token issuance. |
| Python backend | FastAPI + SQLModel | CRUD for users, vehicles, tickets, fees, payments, lot spaces. Provides `/api/core/**` routes consumed by the Web UI. |
| Web UI | Vanilla HTML/CSS/JS | Authenticates against the Java API, renders operational KPIs from the Python API, and allows operators to manage vehicle records. |

Both APIs expose automatic OpenAPI/Swagger documentation (SpringDoc for Java, FastAPI docs at `/docs`).

## Database configuration

### Java backend (MySQL)

| Variable | Default | Description |
| --- | --- | --- |
| `SPRING_DATASOURCE_URL` | `jdbc:mysql://localhost:3306/parking_db` | JDBC URL for the authentication database. |
| `SPRING_DATASOURCE_USERNAME` | `admin` | Database user with DDL/DML permissions. |
| `SPRING_DATASOURCE_PASSWORD` | `admin123` | Database password. |
| `APP_JWT_SECRET` | `changeme-in-prod` | Secret key used to sign JWTs. |

`src/main/resources/application.properties` documents the same settings and can be overridden through environment variables when running with Maven or Docker.

### Python backend (PostgreSQL)

The FastAPI service reads its connection from environment variables at startup. A single `DATABASE_URL` takes precedence; otherwise individual parameters are used.

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql://admon:admon@localhost:5432/parking` | Full SQLAlchemy connection string. |
| `DB_HOST` | `localhost` | PostgreSQL host. |
| `DB_PORT` | `5432` | Port where PostgreSQL listens. |
| `DB_USER` | `admon` | Database user. |
| `DB_PASSWORD` | `admon` | User password. |
| `DB_NAME` | `parking` | Database name. |
| `SQL_ECHO` | `false` | Set to `true` to log SQL statements. |

For automated tests we rely on `sqlite:///:memory:` and the code automatically enables the proper SQLModel connection arguments.

## API reference

### Java authentication API (`/api/auth`)

| Method | Path | Body | Description |
| --- | --- | --- | --- |
| `POST` | `/register` | `{ "username", "email", "password", "accessCode" }` | Creates a new user if the supplied access code is valid and unused. |
| `POST` | `/login` | `{ "username", "password" }` | Authenticates the user and returns `{ "token", "type" }`. |

The project ships with a data initializer that creates an admin account, a default `ROLE_USER`, and sample access codes.

### Python core API (`/api/core`)

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/users` | List all registered system operators. |
| `POST` | `/users` | Create a user record for auditing purposes. |
| `GET` | `/users/{id_user}` | Retrieve a specific user. |
| `DELETE` | `/users/{id_user}` | Remove a user. |
| `GET` | `/vehicles` | List vehicles stored in the parking database. |
| `POST` | `/vehicles` | Register a vehicle (plate, type, registration date). |
| `GET` | `/fees` | List fee definitions. |
| `POST` | `/fees` | Create a new fee record. |
| `GET` | `/tickets` | List parking tickets (entry/exit records). |
| `POST` | `/tickets` | Register a new ticket. |
| `GET` | `/payments` | List recorded payments. |
| `POST` | `/payments` | Register a payment. |
| `GET` | `/lotspaces` | List configured lot-space capacities. |
| `POST` | `/lotspaces` | Register lot space capacity entries. |

All routes return JSON payloads defined in `schemas.py`. Extend the API with additional analytics as needed; the Web UI uses the endpoints highlighted above for its dashboard.

## Running the stack

### Java backend

```bash
cd Workshop-3/java-backend
./mvnw spring-boot:run
```

Swagger UI: <http://localhost:8080/swagger-ui.html>

### Python backend

```bash
cd Workshop-3/python-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # add dependencies if needed
uvicorn main:app --reload
```

Interactive docs: <http://localhost:8000/docs>

### Web UI

```bash
cd Workshop-3/web-gui
python -m http.server 8081
```

Open <http://localhost:8081> and use the "Create Account" link to generate an operator with an access code issued by the Java backend. After logging in, the dashboard loads KPIs from the FastAPI service and the "Vehicle registry" tab lets you register vehicles directly against `/api/core/vehicles`.

## Automated tests

| Project | Command | Notes |
| --- | --- | --- |
| Java backend | `./mvnw test` | Includes Mockito-based unit tests for `AuthServiceImpl`. |
| Python backend | `pytest` | Uses FastAPI's `TestClient` with an in-memory SQLite database. |

Both test suites are part of the CI expectations for this workshop. Screenshots of successful runs or CI logs can be attached to submission materials.

## Integration evidence

* The Web UI login form hits `POST /api/auth/login` (Java) and stores the JWT in `localStorage` through `setToken` (see `web-gui/js/api.js`).
* Dashboard metrics and tables call the Python API endpoints (`/api/core/vehicles`, `/api/core/tickets`, `/api/core/lotspaces`) via the helpers in `web-gui/js/api.js`.
* `docs/arquitecture.md` summarises how both services interact and provides `curl` examples to reproduce the same flows without the browser.

Follow the steps above to demonstrate the integration live or capture screenshots for delivery.
