"""
OpenAI service integration with strict typing and error handling.
"""

import logging
from typing import Literal
from openai import AsyncOpenAI, OpenAIError
from app.types import MessageDict
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI service."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
    
    async def complete(
        self,
        messages: list[MessageDict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Get a completion from OpenAI.
        
        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens to generate (overrides default)
            
        Returns:
            Generated text response
            
        Raises:
            OpenAIError: If API call fails
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("OpenAI returned empty response")
            
            return content.strip()
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI completion: {e}")
            raise
    
    async def analyze_intent(
        self,
        text: str,
        history: list[MessageDict],
    ) -> Literal["create_post", "edit_image", "general"]:
        """
        Analyze user intent from text.
        
        Args:
            text: User's message
            history: Recent conversation history
            
        Returns:
            Detected intent
        """
        system_prompt = """You are an intent classifier for an AI social media system.

Analyze the user's message and classify it into one of these intents:
- create_post: User wants to create social media content
- edit_image: User wants to edit an image (but no image uploaded yet)
- general: General conversation or unclear intent

Respond with ONLY the intent name, nothing else."""
        
        messages: list[MessageDict] = [
            {"role": "system", "content": system_prompt},
            *history[-3:],  # Last 3 messages for context
            {"role": "user", "content": text},
        ]
        
        try:
            result = await self.complete(messages, temperature=0.0, max_tokens=20)
            intent = result.lower().strip()
            
            if intent in ["create_post", "edit_image", "general"]:
                return intent  # type: ignore
            
            logger.warning(f"Invalid intent returned: {intent}, defaulting to 'general'")
            return "general"
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return "general"
    
    async def analyze_image_intent(
        self,
        caption: str,
    ) -> Literal["edit_only", "post_only", "both"]:
        """
        Analyze what user wants to do with an image.
        
        Args:
            caption: User's caption/instructions
            
        Returns:
            Detected image intent
        """
        system_prompt = """You are an intent classifier for image-related requests.

Analyze the caption and classify it into one of these intents:
- edit_only: User wants to edit/modify the image
- post_only: User wants to create a social media post about the image
- both: User wants both image editing and post creation

Respond with ONLY the intent name, nothing else."""
        
        messages: list[MessageDict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": caption},
        ]
        
        try:
            result = await self.complete(messages, temperature=0.0, max_tokens=20)
            intent = result.lower().strip()
            
            if intent in ["edit_only", "post_only", "both"]:
                return intent  # type: ignore
            
            logger.warning(f"Invalid image intent: {intent}, defaulting to 'edit_only'")
            return "edit_only"
            
        except Exception as e:
            logger.error(f"Error analyzing image intent: {e}")
            return "edit_only"
    
    async def detect_platforms(self, prompt: str) -> list[str]:
        """
        Detect which platforms user wants content for.
        
        Args:
            prompt: User's request
            
        Returns:
            List of platform names
        """
        system_prompt = """You are a platform detector for social media content creation.

Analyze the request and identify which platforms they want content for.

Available platforms: x, linkedin, instagram, youtube, school

Respond with a comma-separated list or "none" if no specific platform mentioned.
Example: "linkedin" or "x,instagram" or "none"
"""
        
        messages: list[MessageDict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        
        try:
            result = await self.complete(messages, temperature=0.0, max_tokens=50)
            result = result.lower().strip()
            
            if result == "none":
                return []
            
            # Parse and validate platforms
            platforms = [p.strip() for p in result.split(",")]
            valid_platforms = ["x", "twitter", "linkedin", "instagram", "youtube", "school"]
            
            return [
                "x" if p == "twitter" else p
                for p in platforms
                if p in valid_platforms
            ]
            
        except Exception as e:
            logger.error(f"Error detecting platforms: {e}")
            return []
