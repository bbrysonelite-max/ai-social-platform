"""
Post Creator Agent - Orchestrates platform-specific content generation.
"""

import asyncio
import logging
from typing import Any
from app.types import MessageDict, Platform
from app.services.openai_service import OpenAIService
from app.agents.platform_agents.x_agent import XAgent
from app.agents.platform_agents.linkedin_agent import LinkedInAgent
from app.agents.platform_agents.instagram_agent import InstagramAgent
from app.agents.platform_agents.youtube_agent import YouTubeAgent
from app.agents.platform_agents.school_agent import SchoolAgent

logger = logging.getLogger(__name__)


class PostCreatorAgent:
    """
    Orchestrates multi-platform content generation.
    
    Detects requested platforms and invokes appropriate agents in parallel.
    """
    
    def __init__(self):
        """Initialize Post Creator agent."""
        self.openai = OpenAIService()
        
        # Initialize all platform agents
        self.agents: dict[str, Any] = {
            "x": XAgent(),
            "twitter": XAgent(),  # Alias
            "linkedin": LinkedInAgent(),
            "instagram": InstagramAgent(),
            "youtube": YouTubeAgent(),
            "school": SchoolAgent(),
        }
    
    async def create_posts(
        self,
        prompt: str,
        history: list[MessageDict],
    ) -> str:
        """
        Create social media posts for requested platforms.
        
        Args:
            prompt: User's content request
            history: Conversation history for context
            
        Returns:
            Formatted response with all generated posts
        """
        logger.info("PostCreator processing request")
        
        # Detect platforms
        platforms = await self.openai.detect_platforms(prompt)
        
        if not platforms:
            return self._no_platform_response()
        
        logger.info(f"Creating posts for platforms: {platforms}")
        
        # Create posts in parallel
        tasks = []
        platform_names = []
        
        for platform in platforms:
            agent = self.agents.get(platform.lower())
            if agent:
                tasks.append(agent.create_post(prompt, history))
                # Normalize platform name for display
                display_name = "X" if platform.lower() in ["x", "twitter"] else platform.title()
                platform_names.append(display_name)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Format response
        response_parts = ["✨ **Generated Posts**\n"]
        
        for platform_name, result in zip(platform_names, results):
            if isinstance(result, Exception):
                logger.error(f"Error generating {platform_name} post: {result}")
                response_parts.append(
                    f"\n❌ **{platform_name}**: Error generating post\n"
                )
            else:
                response_parts.append(f"\n📱 **{platform_name}**\n{result}\n")
        
        return "\n".join(response_parts)
    
    def _no_platform_response(self) -> str:
        """Return response when no platform is detected."""
        return (
            "📝 I can create posts for multiple platforms!\n\n"
            "Which platform(s) would you like?\n"
            "• X (Twitter)\n"
            "• LinkedIn\n"
            "• Instagram\n"
            "• YouTube\n"
            "• School\n\n"
            "Example: 'Create a LinkedIn post about AI automation'"
        )
