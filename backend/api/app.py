from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.utils.logger import logger
from backend.database.manager import db
from backend.api.routers import system, chat, memory, mcp, settings as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events: startup and shutdown."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version} in [{settings.env}] mode...")
    # Initialize database
    db.initialize_db()
    logger.info(f"Database initialized at: {settings.db.sqlite_db_path}")

    yield

    logger.info(f"Shutting down {settings.app_name}...")


def create_app() -> FastAPI:
    """Factory creating and configuring the FastAPI application instance."""
    app = FastAPI(
        title=f"{settings.app_name} Core API",
        version=settings.app_version,
        description="Modular Personal AI Assistant & Operating System Backend",
        lifespan=lifespan,
    )

    # CORS configuration for Vite / mobile / web frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Safe for local assistant execution
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(system.router)
    app.include_router(chat.router)
    app.include_router(memory.router)
    app.include_router(mcp.router)
    app.include_router(settings_router.router)

    @app.get("/")
    async def root():
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "status": "online",
            "docs_url": "/docs",
        }

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "app": settings.app_name,
            "version": settings.app_version,
            "env": settings.env,
        }

    return app


app = create_app()
