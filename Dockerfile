# Stage 1: Build dependencies
FROM python:3.10-alpine as builder

# Install build tools for C-based Python packages (if any)
RUN apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /app
COPY requirements.txt .

# Install dependencies to a temporary path
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

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

# Copy installed libraries from builder stage
COPY --from=builder /install /usr/local

# Switch to non-root user
USER agent

# Default command for development (Port 80)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
