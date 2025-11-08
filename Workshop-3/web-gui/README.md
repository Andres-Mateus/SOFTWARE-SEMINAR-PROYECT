# Parking management Web UI

This static application provides a dashboard and vehicle registry for Workshop 3. It authenticates against the Java backend and loads operational data from the Python backend.

## Features

- **Authentication** – Username/password login using the `/api/auth/login` endpoint. JWTs are persisted in `localStorage`.
- **Account creation** – Registration form that posts to `/api/auth/register` with username, email, password and access code.
- **Dashboard view** – Displays KPIs such as occupied spaces, available spaces, base fee and active vehicles by aggregating `/api/core/tickets`, `/api/core/lotspaces`, `/api/core/vehicles`, and `/api/core/fees` responses.
- **Vehicle registry** – Form to create new vehicle records (`POST /api/core/vehicles`) and list the most recent entries alongside configured lot spaces.

## Running locally

Any static file server works. Example using Python:

```bash
cd Workshop-3/web-gui
python -m http.server 8081
```

Open <http://localhost:8081>. The UI automatically switches between login, registration and application views depending on the JWT stored in the browser.

## Integration points

All API calls are implemented in `js/api.js` and consumed by `js/app.js`. Ensure both backends run locally (Java on port `8080`, FastAPI on `8000`) or adjust the base URLs at the top of `api.js`.

To demonstrate the integration without the browser, follow the `curl` steps described in `../docs/arquitecture.md`.
