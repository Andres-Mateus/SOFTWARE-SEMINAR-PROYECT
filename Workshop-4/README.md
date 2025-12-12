# Workshop 4 Deliverables

This folder documents containerization, acceptance testing, stress testing, and CI/CD for the Parking App (auth-service, core-service, and web frontend).

## 1) Docker Containerization
- Dockerfiles live under `Workshop-4/docker/` for each component:
  - `Dockerfile.auth` builds the Spring Boot auth-service jar.
  - `Dockerfile.core` packages the FastAPI core-service with Uvicorn.
  - `Dockerfile.web` serves the static frontend with nginx.
- Orchestration is handled by `Workshop-4/docker-compose.yml`, which wires MySQL for the auth-service, PostgreSQL for the core-service, and exposes the applications on familiar ports (8080 for auth, 8000 for core, 5500 for the web UI).
- Build and run everything with:
  ```bash
  docker compose -f Workshop-4/docker-compose.yml up --build
  ```

## 2) Acceptance Testing (Cucumber)
- Maven project under `Workshop-4/acceptance-tests` with Cucumber + JUnit + RestAssured.
- Default endpoints:
  - `AUTH_BASE_URL` → `http://localhost:8080/api/auth`
  - `CORE_BASE_URL` → `http://localhost:8000`
- Features cover register/login, parking entry, exit receipt, and overview stats. Run after the stack is up:
  ```bash
  cd Workshop-4/acceptance-tests
  mvn test
  ```
- Capture output to `Workshop-4/results/cucumber-results.txt` (example provided for reference).

## 3) API Stress Testing (JMeter)
- Test plan: `Workshop-4/jmeter/parking-api-stress.jmx` (targets `/api/core/stats/overview`, `/api/core/slots`, `/api/core/sessions`).
- Run in non-GUI mode:
  ```bash
  jmeter -n -t Workshop-4/jmeter/parking-api-stress.jmx -l Workshop-4/jmeter/results/results.jtl
  ```
- Review findings in `Workshop-4/results/jmeter-analysis.md` and inspect the generated JTL for latency/error rates.

## 4) CI/CD (GitHub Actions)
- Workflow at `.github/workflows/ci.yml` runs on push/PR:
  - Java unit tests (`mvn -f Workshop-3/auth-service/pom.xml test`).
  - Python unit tests (`pytest -q Workshop-3/core-service/tests`).
  - Docker image builds for auth/core/web using the Workshop-4 Dockerfiles.
- Notes and troubleshooting tips are in `Workshop-4/results/ci-notes.md`. Check the Actions tab in GitHub to verify runs.

## 5) References
- [Spring Boot Testing Guide](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#features.testing)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing/)
- [Cucumber JVM](https://cucumber.io/docs/guides/10-minute-tutorial/?lang=java)
- [Apache JMeter User Manual](https://jmeter.apache.org/usermanual/index.html)
- [GitHub Actions](https://docs.github.com/en/actions)
