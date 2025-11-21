"""
Main application entry point.

Manages application lifecycle, database initialization, and bot startup.
"""

import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import get_settings
from app.models.database import DatabaseManager
from app.telegram.bot import TelegramBot

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

# Global instances
db_manager: DatabaseManager | None = None
telegram_bot: TelegramBot | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global db_manager, telegram_bot
    
    # Startup
    logger.info("Starting AI Social Media System...")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"User whitelist enabled: {settings.is_user_whitelist_enabled}")
    
    # Initialize database
    db_manager = DatabaseManager(settings.DATABASE_URL, echo=settings.DEBUG)
    db_manager.create_tables()
    logger.info("Database initialized")
    
    # Start Telegram bot
    telegram_bot = TelegramBot(db_manager)
    await telegram_bot.start()
    logger.info("Telegram bot started")
    
    logger.info("✅ System ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Social Media System...")
    if telegram_bot:
        await telegram_bot.stop()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "telegram_bot": "running" if telegram_bot and telegram_bot.application else "stopped",
        "database": "connected" if db_manager else "disconnected",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
