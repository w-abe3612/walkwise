# STEP4 contract scaffold. Final image details are implemented in TASK-ENV-001.
FROM python:3.12-slim AS test
WORKDIR /app
COPY requirements.txt pyproject.toml ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "pytest"]
