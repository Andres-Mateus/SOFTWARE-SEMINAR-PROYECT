# Spring Boot authentication service

This module secures access to the parking management system. It handles user registration through single-use access codes, password hashing, JWT creation, and exposes the `/api/auth` REST endpoints consumed by the Web UI.

## Requirements

- Java 17
- Maven 3.9+
- MySQL 8 (or compatible)

## Running locally

```bash
./mvnw spring-boot:run
```

The API will be available at <http://localhost:8080>. Swagger UI is published at `/swagger-ui.html` and the OpenAPI JSON at `/v3/api-docs`.

Default credentials and data are created by `DataInitializer`:

- Admin username: `admin`
- Admin email: `admin@parking.com`
- Admin password: `Admin@123`
- Access code example: `REGISTER-2025-01`

Adjust the values in `src/main/resources/application.properties` or set these environment variables:

| Variable | Description |
| --- | --- |
| `SPRING_DATASOURCE_URL` | JDBC URL pointing to the MySQL instance. |
| `SPRING_DATASOURCE_USERNAME` / `SPRING_DATASOURCE_PASSWORD` | Credentials for the database. |
| `APP_JWT_SECRET` | Secret used to sign issued JWT tokens. |
| `APP_JWT_EXPIRATION` | Token validity in milliseconds. |

## Testing

```
./mvnw test
```

The suite includes Mockito-based unit tests for `AuthServiceImpl`, ensuring that registration validates unique usernames/emails, marks access codes as used, and delegates authentication correctly when issuing JWT tokens.

## REST endpoints

- `POST /api/auth/register` – receives `{ "username", "email", "password", "accessCode" }`.
- `POST /api/auth/login` – receives `{ "username", "password" }` and returns `{ "token", "type" }`.

These endpoints are consumed directly by the front-end (`web-gui/js/api.js`).
