# FastAPI Batch Executor

A FastAPI-based microservice designed for executing AI tasks, either individually or in batches, using the **Google Gemini API** (`gemini-2.0-flash`). It supports both synchronous and asynchronous execution modes, utilizing **AWS S3** for result consolidation and **Webhooks** for notification.

## Features

- **Batch Execution**: Run multiple AI tasks in parallel.
- **Sync/Async Modes**: Get results immediately or process in the background.
- **S3 Integration**: Automatically consolidates and uploads results to AWS S3.
- **Webhook Notifications**: Notifies external services upon completion of async tasks.
- **Concurrency Control**: Built-in semaphore to respect Gemini API rate limits.
- **Daily Logging**: Timed rotating logs for easy maintenance.

## Project Structure

```text
app/
├── api/            # API Route handlers
├── schemas/        # Pydantic models for request/response
├── services/       # Logic for Gemini, S3, and Webhooks
├── utils/          # Helper functions
├── config.py       # Configuration and Environment variables
├── logger.py       # Logging setup
└── main.py         # Application entry point
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
./start.sh
```
Or run directly with uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 60062
```

### API Endpoints

#### 1. Health Check
`GET /health`
Returns the status and current port.

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

### Formatting
Run the formatting script to maintain code style:
```bash
./format.sh
```

### Verification
Verify the installation and server status:
```bash
python verify.py
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API Key | - |
| `AWS_ACCESS_KEY_ID` | AWS Access Key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key | - |
| `AWS_REGION` | AWS Region for S3 | `ap-southeast-1` |
| `S3_BUCKET_NAME` | S3 Bucket name | - |
| `CONCURRENCY_LIMIT` | Parallel requests to Gemini | `3` |
| `APP_PORT` | Application Port | `60062` |
| `DEBUG` | Enable reload mode | `False` |

## License
MIT
