"""YouTube content generation agent."""

import logging
from app.types import MessageDict, Platform
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class YouTubeAgent:
    """Generates YouTube-optimized titles and descriptions."""
    
    platform: Platform = Platform.YOUTUBE
    
    def __init__(self):
        """Initialize YouTube agent."""
        self.openai = OpenAIService()
    
    async def create_post(self, prompt: str, history: list[MessageDict]) -> str:
        """Create YouTube title and description."""
        logger.info("YouTubeAgent creating content")
        
        system_prompt = """You are an expert YouTube content creator.

YOUTUBE CONTENT STRUCTURE:
1. Title (60-70 characters, attention-grabbing, keyword-rich)
2. Description (SEO-optimized, 150-300 words)

TITLE: Clear value, includes keywords, creates curiosity
DESCRIPTION: First 2-3 lines crucial, natural keywords, timestamps if relevant, CTA

Format as:
**Title:** [title]

**Description:**
[description]

TONE: Enthusiastic, clear, SEO-conscious

Create YouTube title and description."""
        
        messages: list[MessageDict] = [
            {"role": "system", "content": system_prompt},
            *history[-3:],
            {"role": "user", "content": prompt},
        ]
        
        try:
            content = await self.openai.complete(messages, temperature=0.7, max_tokens=800)
            logger.info("YouTubeAgent content created")
            return content
        except Exception as e:
            logger.error(f"Error creating YouTube content: {e}")
            raise
