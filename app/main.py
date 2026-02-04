"""
Main entry point for the fastapi-batch-executor application.
This module initializes the FastAPI app, configures global settings,
registers API routers, and defines the application's startup behavior.
"""

import uvicorn
from fastapi import FastAPI

from app.api.executor import router as executor_router
from app.core.config import Config
from app.core.logger import logger

# Initialize the FastAPI application
# Sets metadata like title, description, and version for API documentation (Swagger/Redoc)
app = FastAPI(
    title="fastapi-batch-executor",
    description="Microservice for handling single and batch AI tasks using Google Gemini and AWS S3",
    version="1.0.0",
)

# Register API routes
# Includes the executor router under the '/batch' prefix for all AI processing endpoints
app.include_router(executor_router, prefix="/batch", tags=["Batch Executor"])


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify that the service is running and healthy.

    Returns:
        dict: A dictionary containing the service status, project name, and active port.
    """
    return {
        "status": "healthy",
        "project": "fastapi-batch-executor",
        "port": Config.APP_PORT,
    }


if __name__ == "__main__":
    # Log the application startup information, including the port it will listen on
    logger.info(f"Starting fastapi-batch-executor on port: {Config.APP_PORT}")

    # Start the Uvicorn server to host the FastAPI application
    # host: "0.0.0.0" allows external access to the container/machine
    # port: Configured port from environment variables or default settings
    # reload: Enabled in debug mode for automatic code refresh during development
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=Config.APP_PORT, reload=Config.DEBUG
    )
