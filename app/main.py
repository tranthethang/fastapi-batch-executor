from fastapi import FastAPI
from app.api.v1.executor import router as executor_router

app = FastAPI(
    title="fastapi-batch-executor",
    description="Microservice for handling single and batch AI tasks with S3 and Webhook support",
    version="1.0.0"
)

# Register Routers
app.include_router(executor_router, prefix="/v1/batch", tags=["Batch Executor"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)