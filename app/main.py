import uvicorn
import os
from fastapi import FastAPI
from app.api.v1.executor import router as executor_router
from app.core.config import settings
from app.core.logging_config import setup_logging

# Khởi tạo logging
setup_logging()

app = FastAPI(
    title="fastapi-batch-executor",
    description="Microservice for handling single and batch AI tasks",
    version="1.0.0"
)

# Đăng ký router
app.include_router(executor_router, prefix="/v1/batch", tags=["Batch Executor"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "project": "fastapi-batch-executor",
        "port": settings.APP_PORT
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=settings.APP_PORT, 
        reload=settings.DEBUG
    )