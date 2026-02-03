import uvicorn
from fastapi import FastAPI

from app.api.executor import router as executor_router
from app.core.config import Config
from app.core.logger import logger

app = FastAPI(
    title="fastapi-batch-executor",
    description="Microservice for handling single and batch AI tasks",
    version="1.0.0",
)

# Đăng ký router
app.include_router(executor_router, prefix="/batch", tags=["Batch Executor"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "project": "fastapi-batch-executor",
        "port": Config.APP_PORT,
    }


if __name__ == "__main__":
    logger.info(f"Starting fastapi-batch-executor on port: {Config.APP_PORT}")
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=Config.APP_PORT, reload=Config.DEBUG
    )
