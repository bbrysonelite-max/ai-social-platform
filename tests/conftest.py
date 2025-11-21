"""
Shared test fixtures and configuration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.types import MessageDict
from app.models.database import DatabaseManager, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return "This is a generated response from OpenAI"


@pytest.fixture
def mock_openai_service(mock_openai_response):
    """Mock OpenAI service."""
    service = AsyncMock()
    service.complete = AsyncMock(return_value=mock_openai_response)
    service.analyze_intent = AsyncMock(return_value="create_post")
    service.analyze_image_intent = AsyncMock(return_value="edit_only")
    service.detect_platforms = AsyncMock(return_value=["linkedin"])
    return service


@pytest.fixture
def sample_conversation_history() -> list[MessageDict]:
    """Sample conversation history for testing."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help you?"},
        {"role": "user", "content": "Create a LinkedIn post about AI"},
    ]


@pytest.fixture
def test_db_manager():
    """Create an in-memory test database."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    
    db_manager = DatabaseManager("sqlite:///:memory:", echo=False)
    db_manager.engine = engine
    db_manager.SessionLocal = sessionmaker(bind=engine)
    
    yield db_manager
    
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_prompts():
    """Sample prompts for testing."""
    return {
        "linkedin": "Create a LinkedIn post about AI automation",
        "x": "Write a tweet about productivity",
        "instagram": "Make an Instagram caption about travel",
        "youtube": "Create a YouTube description for a Python tutorial",
        "school": "Write a School community post about learning",
        "multi_platform": "Create posts for X and LinkedIn about remote work",
    }
