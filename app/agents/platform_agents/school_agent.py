"""School community content generation agent."""

import logging
from app.types import MessageDict, Platform
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class SchoolAgent:
    """Generates School community-optimized posts."""
    
    platform: Platform = Platform.SCHOOL
    
    def __init__(self):
        """Initialize School agent."""
        self.openai = OpenAIService()
    
    async def create_post(self, prompt: str, history: list[MessageDict]) -> str:
        """Create a School community post."""
        logger.info("SchoolAgent creating post")
        
        system_prompt = """You are an expert community manager for School platform.

SCHOOL POST CHARACTERISTICS:
- Community-focused and collaborative
- Educational and value-driven
- Encourages discussion
- Friendly, supportive tone
- Clear structure with headings
- 150-250 words
- 2-4 emojis for visual breaks
- Often ends with "Love an automation, Jack"

TONE: Warm, expert but approachable, community-oriented

Create a School community post."""
        
        messages: list[MessageDict] = [
            {"role": "system", "content": system_prompt},
            *history[-3:],
            {"role": "user", "content": prompt},
        ]
        
        try:
            post = await self.openai.complete(messages, temperature=0.7, max_tokens=700)
            
            # Add signature if not present
            if "Love an automation" not in post:
                post += "\n\nLove an automation,\nJack"
            
            logger.info("SchoolAgent post created")
            return post
            
        except Exception as e:
            logger.error(f"Error creating School post: {e}")
            raise
