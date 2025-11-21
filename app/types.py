"""
Type definitions for the AI Social Media Automation System.

This module defines all custom types, enums, and type aliases used throughout
the application. It serves as the single source of truth for type contracts.
"""

from enum import Enum
from typing import Literal, TypedDict, Protocol
from datetime import datetime


# ============================================================================
# Enums
# ============================================================================

class MessageRole(str, Enum):
    """Role of a message in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Type of message content."""
    TEXT = "text"
    IMAGE = "image"
    MIXED = "mixed"


class Platform(str, Enum):
    """Supported social media platforms."""
    X = "x"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    SCHOOL = "school"


class Intent(str, Enum):
    """User intent categories."""
    CREATE_POST = "create_post"
    EDIT_IMAGE = "edit_image"
    GENERAL = "general"


class ImageIntent(str, Enum):
    """Intent for image-related requests."""
    EDIT_ONLY = "edit_only"
    POST_ONLY = "post_only"
    BOTH = "both"


# ============================================================================
# Type Aliases
# ============================================================================

ConversationID = int
UserID = int
ChatID = int
FileID = str
ImageURL = str


# ============================================================================
# TypedDict Definitions
# ============================================================================

class MessageDict(TypedDict):
    """Structure of a message in conversation history."""
    role: MessageRole
    content: str


class ConversationContext(TypedDict):
    """Context information for a conversation."""
    conversation_id: ConversationID
    user_id: UserID
    chat_id: ChatID
    history: list[MessageDict]


class PlatformPostResult(TypedDict):
    """Result from a platform-specific agent."""
    platform: Platform
    content: str
    success: bool
    error: str | None


class ImageEditResult(TypedDict):
    """Result from image editing operation."""
    success: bool
    edited_image_url: ImageURL | None
    version_number: int
    error: str | None


class ImageVersionRecord(TypedDict):
    """Record of an image version."""
    original_image_id: FileID
    drive_file_id: FileID
    imagebb_url: ImageURL
    replicate_output_url: ImageURL
    edit_instruction: str
    version_number: int
    created_at: datetime


# ============================================================================
# Protocols (Structural Subtyping)
# ============================================================================

class PlatformAgent(Protocol):
    """Protocol for platform-specific content generation agents."""
    
    platform: Platform
    
    async def create_post(self, prompt: str, history: list[MessageDict]) -> str:
        """
        Create a platform-specific post.
        
        Args:
            prompt: User's content request
            history: Recent conversation history for context
            
        Returns:
            Generated post content
            
        Raises:
            Exception: If post generation fails
        """
        ...


class ExternalService(Protocol):
    """Protocol for external service integrations."""
    
    async def health_check(self) -> bool:
        """
        Check if the service is available.
        
        Returns:
            True if service is healthy, False otherwise
        """
        ...


# ============================================================================
# Literal Types for Configuration
# ============================================================================

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
DatabaseType = Literal["sqlite", "postgresql"]
AIModel = Literal["gpt-4-turbo-preview", "gpt-3.5-turbo", "claude-3-sonnet-20240229"]
