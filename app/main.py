import uvicorn
import os
from fastapi import FastAPI
from app.api.v1.executor import router as executor_router
from app.core.config import settings

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
    # Logic: Ưu tiên APP_PORT từ .env, nếu không có (None/0) thì dùng 80
    run_port = settings.APP_PORT if settings.APP_PORT else 80
    
    # Reload=True chỉ nên dùng trong môi trường development
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=int(run_port), 
        reload=True
    )