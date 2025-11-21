"""
X (Twitter) content generation agent.

Creates concise, engaging posts for X with strict character limits.
"""

import logging
from app.types import MessageDict, Platform
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class XAgent:
    """
    Generates X-optimized content.
    
    Characteristics:
    - Maximum 280 characters (STRICT)
    - Punchy and attention-grabbing
    - Clear value proposition
    - 1-3 hashtags
    - Conversational tone
    """
    
    platform: Platform = Platform.X
    MAX_LENGTH: int = 280
    
    def __init__(self):
        """Initialize X agent."""
        self.openai = OpenAIService()
    
    async def create_post(self, prompt: str, history: list[MessageDict]) -> str:
        """
        Create an X post.
        
        Args:
            prompt: User's content request
            history: Recent conversation history for context
            
        Returns:
            Generated X post (under 280 characters)
            
        Raises:
            Exception: If post generation fails
        """
        logger.info("XAgent creating post")
        
        system_prompt = """You are an expert X (Twitter) content creator.

X POST REQUIREMENTS:
- MAXIMUM 280 characters (STRICT LIMIT)
- Strong, attention-grabbing opening
- Concise and punchy
- Clear value or insight
- Conversational and authentic
- 1-3 hashtags (included in character count)
- Use line breaks for readability

TONE: Confident, direct, engaging

Create an X post. MUST be under 280 characters."""
        
        messages: list[MessageDict] = [
            {"role": "system", "content": system_prompt},
            *history[-3:],
            {"role": "user", "content": prompt},
        ]
        
        try:
            post = await self.openai.complete(messages, temperature=0.7, max_tokens=150)
            
            # Enforce character limit
            if len(post) > self.MAX_LENGTH:
                logger.warning(
                    f"X post exceeds {self.MAX_LENGTH} chars ({len(post)}), truncating"
                )
                post = post[:self.MAX_LENGTH - 3] + "..."
            
            logger.info(f"XAgent post created ({len(post)} chars)")
            return post
            
        except Exception as e:
            logger.error(f"Error creating X post: {e}")
            raise
