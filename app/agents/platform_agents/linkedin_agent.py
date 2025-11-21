"""
LinkedIn content generation agent.

Creates professional, engaging LinkedIn posts optimized for the platform.
"""

import logging
from app.types import MessageDict, Platform
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class LinkedInAgent:
    """
    Generates LinkedIn-optimized content.
    
    Characteristics:
    - Professional yet conversational tone
    - Storytelling and personal insights
    - 150-300 words optimal length
    - 3-5 strategic hashtags
    - Engagement-focused (questions, CTAs)
    """
    
    platform: Platform = Platform.LINKEDIN
    
    def __init__(self):
        """Initialize LinkedIn agent."""
        self.openai = OpenAIService()
    
    async def create_post(self, prompt: str, history: list[MessageDict]) -> str:
        """
        Create a LinkedIn post.
        
        Args:
            prompt: User's content request
            history: Recent conversation history for context
            
        Returns:
            Generated LinkedIn post
            
        Raises:
            Exception: If post generation fails
        """
        logger.info("LinkedInAgent creating post")
        
        system_prompt = """You are an expert LinkedIn content creator.

LINKEDIN POST CHARACTERISTICS:
- Professional yet conversational and authentic
- Start with an attention-grabbing hook
- Use storytelling and personal insights
- Demonstrate thought leadership
- Include actionable insights
- Short paragraphs with line breaks
- End with engagement (question or CTA)
- 3-5 relevant hashtags at end
- 150-300 words optimal

TONE: Professional, confident, educational, engaging

Create a LinkedIn post based on the user's request."""
        
        messages: list[MessageDict] = [
            {"role": "system", "content": system_prompt},
            *history[-3:],
            {"role": "user", "content": prompt},
        ]
        
        try:
            post = await self.openai.complete(messages, temperature=0.7, max_tokens=800)
            logger.info("LinkedInAgent post created successfully")
            return post
        except Exception as e:
            logger.error(f"Error creating LinkedIn post: {e}")
            raise
