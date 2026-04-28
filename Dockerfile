# Stage 1: Build dependencies
FROM python:3.10-alpine AS builder

# Install build tools for C-based Python packages (if any) + curl for uv
RUN apk add --no-cache gcc musl-dev libffi-dev curl

WORKDIR /app

# Install uv (preferred package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy dependency manifest only for better layer caching
COPY pyproject.toml .

# Create venv + install runtime deps only
RUN uv sync --no-dev

# Stage 2: Final Runtime
FROM python:3.10-alpine

ARG WWWUSER
ARG WWWGROUP

WORKDIR /app

# Create 'agent' user and group, handling cases where GID/UID might already exist
RUN if ! grep -q ":${WWWGROUP}:" /etc/group; then \
        addgroup -g ${WWWGROUP} agent; \
    fi && \
    if ! grep -q ":${WWWUSER}:" /etc/passwd; then \
        adduser -D -u ${WWWUSER} -G $(grep ":${WWWGROUP}:" /etc/group | cut -d: -f1) agent; \
    fi

# Copy virtualenv from builder stage
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

# Switch to non-root user
USER agent

# Default command for development (Port 80)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
