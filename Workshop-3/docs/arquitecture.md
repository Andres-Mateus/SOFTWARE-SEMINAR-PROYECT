# Architecture Snapshot

The Parking Platform is composed of:

1. **Java authentication service (`java-backend`)** – handles registration with access codes, JWT issuance, and admin tooling.
2. **Python core service (`python-backend`)** – orchestrates slots, tickets, payments, and exposes dashboard endpoints.
3. **Web GUI (`web-gui`)** – static SPA that authenticates against the Java service and consumes the Python API.

Communication happens over HTTP/JSON. The Web UI stores the JWT returned by the Java service and forwards it via the `Authorization` header to the Python service. Both backends expose Swagger/OpenAPI documentation for quick inspection.
