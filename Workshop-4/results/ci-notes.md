# CI/CD Notes

The GitHub Actions workflow `.github/workflows/ci.yml` runs on every push and pull request. It verifies the backends and container builds used in Workshop 3 and 4:

1. Installs Python 3.11 and the FastAPI dependencies, then executes `pytest -q Workshop-3/core-service/tests`.
2. Builds and tests the Java auth-service with `mvn -f Workshop-3/auth-service/pom.xml test` on JDK 17.
3. Builds Docker images for the auth-service, core-service, and web frontend using the Dockerfiles stored under `Workshop-4/docker/`.

Check the **Actions** tab in GitHub to confirm successful runs or inspect logs when a check fails.
