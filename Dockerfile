
FROM python:3.12-slim-bookworm

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD pipegate/ /app/pipegate
ADD uv.lock /app
ADD pyproject.toml /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

# Workers must be one atm.
CMD ["uvicorn", "pipegate.server:main", "--host", "0.0.0.0", "--port", "8000", "--factory", "--workers", "1"]
