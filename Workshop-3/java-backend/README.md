# Java Authentication Service

Spring Boot 3 service that issues JWT tokens, handles registration through single-use access codes, and exposes admin tooling for managing codes.

## Stack

- Java 17
- Spring Boot 3.1
- Spring Security (JWT)
- MySQL 8 (default) – configurable via environment variables
- Maven Wrapper

## Running locally

```bash
./mvnw spring-boot:run
```

Environment variables (override defaults in `application.properties`):

```bash
export SPRING_DATASOURCE_URL=jdbc:mysql://localhost:3306/parking_db
export SPRING_DATASOURCE_USERNAME=admin
export SPRING_DATASOURCE_PASSWORD=admin123
export APP_JWT_SECRET=ReplaceThisSecretForProd
```

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Creates a new user using a valid access code. |
| `POST` | `/api/auth/login` | Logs in by e-mail and returns a JWT + user profile. |
| `POST` | `/api/admin/access-code/generate` | Admin-only helper to mint new access codes. |

### `POST /api/auth/register`

```json
{
  "email": "user@example.com",
  "password": "StrongPass#123",
  "accessCode": "REGISTER-2025-01",
  "username": "optionalAlias"
}
```

Response `200 OK`:

```json
{ "message": "User created successfully" }
```

When the `username` field is omitted the service derives a unique username from the e-mail prefix.

### `POST /api/auth/login`

```json
{
  "email": "user@example.com",
  "password": "StrongPass#123"
}
```

Response `200 OK`:

```json
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

## Default data

`DataInitializer` seeds the following resources when the application starts:

- `admin@parking.com` / `Admin@123` with role `ROLE_ADMIN`
- Access code `REGISTER-2025-01` (30-day validity)

## Testing

```bash
./mvnw test
```

`JwtUtilTest` validates token generation, extraction, and tampering detection using Spring's test framework.
