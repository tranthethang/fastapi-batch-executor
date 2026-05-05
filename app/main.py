"""
Main entry point for the fastapi-batch-executor application.
This module initializes the FastAPI app, configures global settings,
registers API routers, and defines the application's startup behavior.
"""

import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyflow_ai_stack.schemas.models import HealthResponse

from app.api.executor import router as executor_router
from app.core.config import settings
from app.core.logger import logger
from app.services import health_service

# Initialize the FastAPI application
# Sets metadata like title, description, and version for API documentation (Swagger/Redoc)
app = FastAPI(
    title="fastapi-batch-executor",
    description="Microservice for handling single and batch AI tasks using Google Gemini and AWS S3",
    version="1.0.0",
    root_path=os.getenv("ROOT_PATH", ""),
    openapi_url=settings.OPENAPI_JSON_PATH,
    docs_url=settings.SWAGGER_UI_PATH,
    redoc_url=settings.REDOC_PATH,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
# Includes the executor router under the '/batch' prefix for all AI processing endpoints
app.include_router(executor_router, prefix="/batch", tags=["Batch Executor"])


@app.get("/health", response_model=HealthResponse, response_model_exclude_none=True)
async def health_check(depends: int = 0):
    """
    Health check endpoint to verify that the service is running and healthy.

    Args:
        depends (int): Whether to check dependencies (1) or not (0).

    Returns:
        dict: A dictionary containing the service status, project name, and active port.
    """
    return await health_service.check_health(depends=depends)


if __name__ == "__main__":
    # Log the application startup information, including the port it will listen on
    logger.info(f"Starting fastapi-batch-executor on port: {settings.APP_PORT}")

    # Start the Uvicorn server to host the FastAPI application
    # host: "0.0.0.0" allows external access to the container/machine
    # port: Configured port from environment variables or default settings
    # reload: Enabled in debug mode for automatic code refresh during development
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=settings.APP_PORT, reload=settings.DEBUG
    )
