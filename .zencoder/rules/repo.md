---
description: Repository Information Overview
alwaysApply: true
---

# fastapi-batch-executor Information

## Summary
**fastapi-batch-executor** is a FastAPI-based microservice designed for executing AI tasks, either individually or in batches. It utilizes the **Google Gemini API** (specifically `gemini-2.0-flash`) for content generation and **AWS S3** for storing consolidated results. The service supports both synchronous and asynchronous execution modes, using background tasks and webhooks for notification upon completion.

## Structure
The project follows a standard FastAPI structure:
- [./app/](./app/): Main application package.
  - [./app/main.py](./app/main.py): Entry point, application initialization, and health check.
  - [./app/api/v1/](./app/api/v1/): API routers and request/response models.
  - [./app/core/](./app/core/): Core configurations and settings management.
  - [./app/services/](./app/services/): Business logic and external service integrations (Gemini, S3, Webhooks).
- [./requirements.txt](./requirements.txt): Python dependency list.
- [./.env.example](./.env.example): Template for environment variables.

## Language & Runtime
**Language**: Python  
**Version**: Python 3.x (assumed from async/await usage)  
**Build System**: pip  
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- **fastapi**: Web framework.
- **uvicorn**: ASGI server.
- **pydantic-settings**: Environment variable management.
- **google-generativeai**: Google Gemini API client.
- **aioboto3**: Asynchronous AWS SDK for S3 operations.
- **httpx**: Asynchronous HTTP client for webhooks.
- **python-multipart**: Support for multi-part form data.

## Build & Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage & Operations
**Key Commands**:
```bash
# Run the application locally (defaults to port 60062 if configured)
python -m app.main
```

**Main Entry Point**: [./app/main.py](./app/main.py)  
**API Endpoints**:
- `GET /health`: Health check endpoint.
- `POST /v1/batch/run`: Execute single or batch AI tasks.
  - `mode="sync"`: Returns results immediately.
  - `mode="async"`: Initiates background processing and notifies via `webhook_url`.

**Configuration**:
The application requires several environment variables (see [./.env.example](./.env.example)):
- `GEMINI_API_KEY`: API key for Google Gemini.
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `S3_BUCKET_NAME`: AWS credentials and S3 configuration.
- `CONCURRENCY_LIMIT`: Limits parallel requests to Gemini (default: 3).

## Testing
No testing framework or test files were identified in the repository.
