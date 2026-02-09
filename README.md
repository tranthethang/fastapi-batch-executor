# FastAPI Batch Executor

A FastAPI-based microservice designed for executing AI tasks, either individually or in batches, using the **Google Gemini API** (`gemini-2.0-flash`). Built on top of the **pyflow-ai-stack**, it supports both synchronous and asynchronous execution modes, utilizing **AWS S3** for result consolidation, **Redis** for state management, and **Webhooks** for notification.

## Features

- **Batch Execution**: Run multiple AI tasks in parallel.
- **Sync/Async Modes**: Get results immediately or process in the background.
- **S3 Integration**: Automatically consolidates and uploads results to AWS S3.
- **Webhook Notifications**: Notifies external services upon completion of async tasks.
- **Redis Support**: Integrated for health checks and potential state management.
- **Built-in Health Checks**: Detailed health monitoring for Gemini, S3, and Redis.
- **Concurrency Control**: Respects Gemini API rate limits with configurable concurrency.

## Project Structure

```text
app/
├── api/            # API Route handlers (Executor)
├── core/           # Core configurations and logging
├── schemas/        # Pydantic models for request/response
├── services/       # Business logic (Gemini, S3, Webhook, Executor)
└── main.py         # Application entry point

bin/                # Operational shell scripts
tests/              # Comprehensive test suite
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fastapi-batch-executor
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

## Usage

### Starting the Server
Use the provided shell script:
```bash
./bin/start.sh
```
Or run directly with uvicorn:
```bash
python -m app.main
```

### API Endpoints

#### 1. Health Check
`GET /health?depends=1`
Returns the status of the service and its dependencies (Gemini, S3, Redis).

#### 2. Execute Tasks
`POST /batch/run`

**Request Body Example**:
```json
{
  "project_id": "test-project-001",
  "mode": "async",
  "global_files": [
    {
      "uri": "https://generativelanguage.googleapis.com/v1beta/files/...",
      "mime_type": "application/pdf"
    }
  ],
  "tasks": [
    {
      "task_id": "task-1",
      "prompt": "Summarize this document."
    }
  ],
  "webhook_url": "https://your-webhook.com/callback",
  "s3_path_prefix": "ai-output/"
}
```

## Operations

### Testing
Run the test suite using the provided script:
```bash
./bin/test.sh
```

### Formatting
Maintain code style with:
```bash
./bin/format.sh
```

### Verification
Verify service health:
```bash
./bin/verify.sh
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API Key | - |
| `GEMINI_MODEL` | Gemini Model version | `gemini-2.0-flash` |
| `AWS_ACCESS_KEY_ID` | AWS Access Key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key | - |
| `AWS_REGION` | AWS Region for S3 | `us-east-1` |
| `S3_BUCKET_NAME` | S3 Bucket name | - |
| `S3_ENDPOINT_URL` | Optional custom S3 endpoint | - |
| `REDIS_HOST` | Redis server host | `localhost` |
| `REDIS_PORT` | Redis server port | `6379` |
| `CONCURRENCY_LIMIT` | Parallel requests to Gemini | `3` |
| `APP_PORT` | Application Port | `60062` |

## License
MIT
