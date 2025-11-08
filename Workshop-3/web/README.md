# Parking Management Web UI

This folder contains the Web UI for the Workshop-3 Parking Management System.

It is a framework-free, professional-looking frontend built with:

* HTML5
* CSS3
* Vanilla JavaScript (ES6+)

It is designed specifically for the workshop architecture:

* auth-service (Java / Spring Boot) – authentication & registration using unique access codes.
* core-service (Python / FastAPI) – parking logic (entries, exits, slots, fees, stats).
* web (this folder) – management console for operators/admins.

No bundlers, no React, no Vite — simple to run, easy to review, and cleanly structured.

---

1. Features Overview

---

1.1 Authentication

* Login via auth-service:

  * Sends email + password to /api/auth/login.
  * On success:

    * Stores access_token (JWT) and user info in localStorage.
    * Unlocks protected sections (Dashboard & Vehicles).
* Logout:

  * Clears token and user.
  * Returns to login screen.

1.2 Registration with Unique Access Code

* Register page for creating new accounts:

  * Fields: email, password, access_code.
  * Uses POST /api/auth/register.
  * Only users with a valid and unused access code can sign up.
  * On success: shows confirmation and redirects back to login.

1.3 Dashboard (Protected)

Uses core-service to display an overview of the parking lot:

* KPIs:

  * Occupied spaces
  * Free spaces
  * Active vehicles
  * Current rate per minute
* Occupancy (last 24h):

  * Visualized as a simple horizontal bar.
* Recent activity:

  * List of recent sessions (entries/exits).

If core-service is unavailable, the UI falls back to demo data so the layout remains presentable.

1.4 Vehicles Management (Protected)

Designed for parking operators:

* Register Entry:

  * Mode: Entrada.
  * Input: vehicle plate.
  * Calls POST /api/core/entries.
  * Shows assigned slot in the UI.
* Register Exit:

  * Mode: Salida.
  * Input: vehicle plate.
  * Calls POST /api/core/exits.
  * Expects backend to compute:

    * Total minutes parked.
    * Amount to pay (based on rate per minute).
  * UI message:

    * “Salida registrada. X min · Total $Y.YY.”
* Parking Slots Table:

  * Uses GET /api/core/slots.
  * Shows each slot:

    * Code
    * Status (Occupied / Free)
    * Plate (if occupied).
* Recent Activity (Vehicles):

  * Uses GET /api/core/sessions.
  * Shows latest movements.

If the backend is unavailable, the page shows sample slots and messages indicating demo mode.

1.5 Consistent Branding

* Navbar logo: circular P.
* Tab icon (favicon.svg): same style as navbar logo.
* Clean, dashboard-style layout suitable for academic/professional submission.

---

2. Folder Structure

---

web/
├─ index.html          - Main entry: login, register, dashboard, vehicles
├─ favicon.svg         - Tab icon matching the navbar logo (P)
├─ css/
│  └─ style.css        - Styling (layout, navbar, cards, tables, etc.)
└─ js/
├─ api.js           - API helpers for auth-service and core-service
└─ app.js           - UI logic (routing, auth state, forms, rendering)

---

3. How It Works (High-Level Flow)

---

3.1 Authentication Flow

1. User opens index.html.
2. The UI checks localStorage:

   * If there is a token → loads Dashboard.
   * If not → shows Login.
3. On login:

   * POST AUTH_API_URL + /login with { email, password }.
   * Expects { access_token, user: { email, role } }.
   * Saves token and user in localStorage.
   * Shows protected views.

3.2 Registration with Access Code

1. From login, user clicks “Create your account” link.
2. On the Register page:

   * User enters email, password, access_code.
   * POST AUTH_API_URL + /register.
3. Backend responsibilities:

   * Validate the access_code (exists, unused, not expired).
   * Create user.
4. On success:

   * UI displays success message and suggests logging in.

3.3 Authorization with core-service

For all calls to core-service, app.js uses apiFetch():

* Reads token from localStorage.
* Adds:
  Authorization: Bearer <token>
* core-service validates the JWT:

  * If valid → responds with data.
  * If invalid/expired → should return 401 (UI can be extended to force logout).

---

4. API Contracts (Expected)

---

These endpoints are expected by the current UI. Adjust either side consistently if your implementation differs.

4.1 auth-service

Base URL (in js/api.js):

AUTH_API_URL = '[http://localhost:8080/api/auth](http://localhost:8080/api/auth)'

POST /login

Request:
{
"email": "[user@parking.com](mailto:user@parking.com)",
"password": "secret"
}

Response:
{
"access_token": "JWT_TOKEN_HERE",
"user": {
"email": "[user@parking.com](mailto:user@parking.com)",
"role": "OPERATOR"
}
}

POST /register

Request:
{
"email": "[user@parking.com](mailto:user@parking.com)",
"password": "secret",
"access_code": "UNIQUE-CODE-123"
}

Response example:
{
"id": 1,
"email": "[user@parking.com](mailto:user@parking.com)",
"role": "OPERATOR"
}

If code is invalid / used / expired → return 4xx (the UI shows an error).

4.2 core-service

Base URL (in js/api.js):

CORE_API_URL = '[http://localhost:8000/api/core](http://localhost:8000/api/core)'

All endpoints below require:

Authorization: Bearer <JWT_FROM_auth-service>

GET /stats/overview

Example response:
{
"occupied": 20,
"free": 30,
"activeVehicles": 18,
"currentRatePerMinute": 0.05,
"occupancyPercent": 40.0
}

GET /slots

Example response:
[
{ "code": "A01", "occupied": true,  "plate": "ABC-123" },
{ "code": "A02", "occupied": false, "plate": null }
]

GET /sessions?limit=5&order=desc

Example response:
{
"items": [
{
"id": 1,
"plate": "ABC-123",
"check_in_at": "2025-11-07T10:00:00Z",
"check_out_at": null
}
]
}

(You can also return a plain array if you adapt the UI accordingly.)

POST /entries

Request:
{
"plate": "ABC-123"
}

Response example:
{
"session_id": 1,
"plate": "ABC-123",
"slot_code": "A01",
"check_in_at": "2025-11-07T10:00:00Z"
}

The UI shows:
"Entrada registrada. Espacio: A01."

POST /exits

Request:
{
"plate": "ABC-123"
}

Response example:
{
"session_id": 1,
"plate": "ABC-123",
"minutes": 90,
"amount": 4500.0,
"check_in_at": "2025-11-07T10:00:00Z",
"check_out_at": "2025-11-07T11:30:00Z"
}

The UI shows:
"Salida registrada. 90 min · Total $4500.00."

Note: The fee calculation is done in core-service, not in the frontend.

---

5. Running the Web UI

---

5.1 Prerequisites

Any static file server works. Examples:

* Python 3 built-in server
* Node.js with a simple static server (e.g. npx serve)
* VS Code Live Server
* Nginx / Apache for deployment

5.2 Local Development

From the web directory:

Option 1 (Python):

python -m http.server 8081

Option 2 (Node):

npx serve .

Then open:

[http://localhost:8081](http://localhost:8081)

5.3 Test Without Backend (UI-Only)

To quickly preview the UI layout without a working backend:

1. Start the static server.
2. Open the app in the browser.
3. Open DevTools → Application → Local Storage.
4. Add:

   * Key: token
   * Value: demo-token
5. Refresh.

The app will behave as “logged in” and use demo/demo-fallback data where backend calls fail.

For final submission, use the real auth-service and core-service.

---

6. CORS & Security Notes

---

To work correctly, configure:

auth-service:

* Allow origin: [http://localhost:8081](http://localhost:8081) (or your real frontend URL).
* Allow methods: POST, GET, OPTIONS.
* Allow headers: Content-Type, Authorization.

core-service:

* Same allowed origin.
* All protected endpoints must validate the JWT issued by auth-service.

---

7. Customization

---

You can:

* Change colors and font settings in css/style.css.
* Add institution / course branding.
* Add “Print receipt” or detailed invoice on exit using amount returned by core-service.
* Extend roles (e.g. ADMIN vs OPERATOR) using the roles from JWT payload.

Keep API contracts synchronized with backend changes.

---

8. Summary

---

This Web UI:

* Is minimal, readable, and production-like.
* Implements:

  * Login
  * Registration with unique access code
  * Protected sections
  * Vehicle entry and exit workflows
  * Real-time fee display on exit (based on backend calculation)
  * Occupancy KPIs and recent activity
* Integrates cleanly with auth-service and core-service as defined for Workshop-3.

It is ready to be included in your repository as the official frontend for the Parking Management System.