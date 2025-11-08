# parking_app - Backend (Spring Boot + MySQL + Docker)

## Overview
Backend project for the parking management application built with:
- Spring Boot (Java 17, Maven)
- MySQL (`parking_db`)
- JWT authentication
- Registration using a single-use alphanumeric access code
- Docker + docker-compose (launches MySQL + app)

## Default Credentials
- **MySQL (container):** user `admin` / password `admin123`
- **Database:** `parking_db`
- **Admin user (app):** username `admin`, email `admin@parking.com`, password `Admin@123`
- **Initial access code:** `REGISTER-2025-01` *(single-use)*

## Run with Docker
1. Build and start the containers:
```bash
docker-compose up --build
```
2. Wait for the services to start.  
   Access the Swagger UI at:  
   [http://localhost:8080/swagger-ui.html](http://localhost:8080/swagger-ui.html)

## Notes
- The script `src/main/resources/db/init_db.sql` is mounted into the MySQL container at `/docker-entrypoint-initdb.d/` and runs **only the first time** the `db_data` volume is created.
- Replace `APP_JWT_SECRET` with a secure secret key in production.
- To change database credentials, edit `docker-compose.yml` and `application.properties`, or use environment variables.
