"""Instagram content generation agent."""

import logging
from app.types import MessageDict, Platform
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class InstagramAgent:
    """Generates Instagram-optimized captions."""
    
    platform: Platform = Platform.INSTAGRAM
    
    def __init__(self):
        """Initialize Instagram agent."""
        self.openai = OpenAIService()
    
    async def create_post(self, prompt: str, history: list[MessageDict]) -> str:
        """Create an Instagram caption."""
        logger.info("InstagramAgent creating post")
        
        system_prompt = """You are an expert Instagram content creator.

INSTAGRAM CAPTION CHARACTERISTICS:
- Visual-first: complement the image
- Strong opening hook
- Authentic and relatable
- Storytelling when appropriate
- 3-5 emojis naturally integrated
- Line breaks for readability
- End with CTA or question
- 5-10 relevant hashtags at end
- 125-150 words ideal

TONE: Authentic, personal, inspirational

Create an Instagram caption."""
        
        messages: list[MessageDict] = [
            {"role": "system", "content": system_prompt},
            *history[-3:],
            {"role": "user", "content": prompt},
        ]
        
        try:
            post = await self.openai.complete(messages, temperature=0.7, max_tokens=600)
            logger.info("InstagramAgent post created")
            return post
        except Exception as e:
            logger.error(f"Error creating Instagram post: {e}")
            raise
