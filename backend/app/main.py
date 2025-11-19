from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import agents, workspaces, executions, marketplace, mcp

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME
    }


# Include routers
app.include_router(
    workspaces.router,
    prefix=f"{settings.API_V1_PREFIX}/workspaces",
    tags=["workspaces"]
)

app.include_router(
    agents.router,
    prefix=f"{settings.API_V1_PREFIX}/agents",
    tags=["agents"]
)

app.include_router(
    executions.router,
    prefix=f"{settings.API_V1_PREFIX}/executions",
    tags=["executions"]
)

app.include_router(
    marketplace.router,
    prefix=f"{settings.API_V1_PREFIX}/templates",
    tags=["templates"]
)

app.include_router(
    mcp.router,
    prefix=f"{settings.API_V1_PREFIX}/mcp",
    tags=["mcp"]
)


# System info endpoint
@app.get(f"{settings.API_V1_PREFIX}/system/info")
async def system_info():
    """Get system information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "api_version": "v1"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Agentic AI Platform",
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }

