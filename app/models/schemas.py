"""
Pydantic schemas for data validation and serialization.

These schemas enforce type safety at runtime and provide automatic
validation for data structures throughout the application.
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.types import (
    MessageRole,
    MessageType,
    Platform,
    Intent,
    ImageIntent,
    ConversationID,
    UserID,
    ChatID,
    FileID,
    ImageURL,
)


# ============================================================================
# Configuration Schemas
# ============================================================================

class TelegramConfig(BaseModel):
    """Telegram bot configuration."""
    
    bot_token: str = Field(..., min_length=1, description="Telegram bot API token")
    allowed_user_ids: list[UserID] = Field(
        default_factory=list,
        description="List of authorized user IDs"
    )
    
    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """Validate bot token format."""
        if ":" not in v:
            raise ValueError("Invalid bot token format")
        return v


class AIConfig(BaseModel):
    """AI service configuration."""
    
    openai_api_key: str = Field(..., min_length=1)
    openai_model: str = Field(default="gpt-4-turbo-preview")
    anthropic_api_key: str | None = Field(default=None)
    anthropic_model: str = Field(default="claude-3-sonnet-20240229")
    
    model_config = ConfigDict(frozen=True)


class ExternalServicesConfig(BaseModel):
    """External services configuration."""
    
    imagebb_api_key: str = Field(..., min_length=1)
    replicate_api_token: str = Field(..., min_length=1)
    google_drive_credentials: str | None = Field(default=None)
    google_drive_folder_id: str | None = Field(default=None)


# ============================================================================
# Message Schemas
# ============================================================================

class MessageBase(BaseModel):
    """Base schema for messages."""
    
    role: MessageRole
    content: str = Field(..., min_length=1, max_length=50000)


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    
    conversation_id: ConversationID
    message_type: MessageType = MessageType.TEXT


class MessageResponse(MessageBase):
    """Schema for message responses."""
    
    id: int
    conversation_id: ConversationID
    message_type: MessageType
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Conversation Schemas
# ============================================================================

class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    
    telegram_user_id: UserID
    telegram_chat_id: ChatID


class ConversationResponse(BaseModel):
    """Schema for conversation responses."""
    
    id: ConversationID
    telegram_user_id: UserID
    telegram_chat_id: ChatID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Image Version Schemas
# ============================================================================

class ImageVersionCreate(BaseModel):
    """Schema for creating an image version record."""
    
    conversation_id: ConversationID
    original_image_id: FileID | None = None
    drive_file_id: FileID
    drive_file_name: str | None = None
    imagebb_url: ImageURL | None = None
    replicate_output_url: ImageURL | None = None
    edit_instruction: str
    version_number: int = Field(..., ge=1)


class ImageVersionResponse(BaseModel):
    """Schema for image version responses."""
    
    id: int
    conversation_id: ConversationID
    original_image_id: FileID | None
    drive_file_id: FileID
    imagebb_url: ImageURL | None
    replicate_output_url: ImageURL | None
    edit_instruction: str
    version_number: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Post Generation Schemas
# ============================================================================

class GeneratedPostCreate(BaseModel):
    """Schema for creating a generated post record."""
    
    conversation_id: ConversationID
    platform: Platform
    content: str = Field(..., min_length=1)
    prompt: str | None = None


class GeneratedPostResponse(BaseModel):
    """Schema for generated post responses."""
    
    id: int
    conversation_id: ConversationID
    platform: Platform
    content: str
    prompt: str | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Agent Request/Response Schemas
# ============================================================================

class IntentAnalysisRequest(BaseModel):
    """Request for intent analysis."""
    
    text: str = Field(..., min_length=1)
    history: list[MessageBase] = Field(default_factory=list)


class IntentAnalysisResponse(BaseModel):
    """Response from intent analysis."""
    
    intent: Intent
    confidence: float = Field(..., ge=0.0, le=1.0)


class PlatformDetectionRequest(BaseModel):
    """Request for platform detection."""
    
    prompt: str = Field(..., min_length=1)


class PlatformDetectionResponse(BaseModel):
    """Response from platform detection."""
    
    platforms: list[Platform]


class PostCreationRequest(BaseModel):
    """Request for post creation."""
    
    prompt: str = Field(..., min_length=1)
    platforms: list[Platform]
    history: list[MessageBase] = Field(default_factory=list)


class PostCreationResponse(BaseModel):
    """Response from post creation."""
    
    posts: dict[Platform, str]
    errors: dict[Platform, str] = Field(default_factory=dict)


class ImageEditRequest(BaseModel):
    """Request for image editing."""
    
    image_path: str = Field(..., min_length=1)
    instructions: str = Field(..., min_length=1)
    conversation_id: ConversationID


class ImageEditResponse(BaseModel):
    """Response from image editing."""
    
    success: bool
    edited_image_url: ImageURL | None = None
    version_number: int | None = None
    error: str | None = None
