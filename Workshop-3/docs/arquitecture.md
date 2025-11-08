# Architecture & integration guide

The Workshop 3 solution is composed of three deployable units:

1. **Java authentication API (`java-backend/`)** – Handles onboarding and login.
2. **Python core API (`python-backend/`)** – Provides CRUD operations for parking entities.
3. **Static Web UI (`web-gui/`)** – Authenticates with the Java API and renders operational data from the Python API.

The following diagram summarises the interactions:

```
[Web UI] -- /api/auth/login --> [Java backend] -- JWT --> [Web UI]
   |                                  |
   |                                  '-- accesses MySQL (users, roles, access codes)
   '-- /api/core/... --> [Python backend] -- interacts with PostgreSQL (parking data)
```

## Sequence overview

1. A user registers via `POST /api/auth/register` providing username, email, password, and a valid access code. The Java backend stores the user in MySQL and marks the access code as consumed.
2. The Web UI calls `POST /api/auth/login` with the username/password. On success it stores the JWT returned as `{ token, type }`.
3. Authenticated requests include the JWT in the `Authorization` header. The Java backend issues tokens that remain valid according to `APP_JWT_EXPIRATION`.
4. The Web UI loads dashboard data by calling the Python API: `/api/core/vehicles`, `/api/core/tickets`, `/api/core/lotspaces`, etc. The FastAPI service persists and queries PostgreSQL using SQLModel.

## Reproducing the integration via cURL

Assuming both services are running locally and the Java backend already holds a valid access code (`REGISTER-2025-01`), the following commands replicate the full flow.

### 1. Register a user

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "operator1",
    "email": "operator1@parking.com",
    "password": "Secret123",
    "accessCode": "REGISTER-2025-01"
  }'
```

### 2. Obtain a JWT

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{ "username": "operator1", "password": "Secret123" }'
```

The response payload contains the `token` value used in the next calls.

### 3. Create a vehicle through the Python API

```bash
TOKEN=... # paste the token from the previous step
curl -X POST http://localhost:8000/api/core/vehicles \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "licenseplate": "ABC123",
    "type": "CAR",
    "dateregistered": "2024-05-01"
  }'
```

### 4. Fetch dashboard data

```bash
curl http://localhost:8000/api/core/vehicles \
  -H "Authorization: Bearer $TOKEN"
```

The Web UI executes the same requests (see `web-gui/js/api.js` and `web-gui/js/app.js`), displaying KPIs and vehicle lists based on the responses.

## Testing strategy

- `java-backend/src/test/...` validates the authentication service without hitting the database by mocking repositories, ensuring registration and login flows work as expected.
- `python-backend/tests/` boots the FastAPI app using an in-memory SQLite database to exercise `/api/core/users` end-to-end.

Use `./mvnw test` and `pytest` to verify both layers before demonstrating the application.
