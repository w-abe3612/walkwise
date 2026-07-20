# TASK-ENV-001: Python test stage. Fixed Python version, dependency install,
# pytest collection/normal test execution. No external API/runtime required.
FROM python:3.12-slim AS test
WORKDIR /app
COPY requirements.txt pyproject.toml ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "pytest"]
