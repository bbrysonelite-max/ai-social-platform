"""
Unit tests for platform-specific agents.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.agents.platform_agents.linkedin_agent import LinkedInAgent
from app.agents.platform_agents.x_agent import XAgent
from app.agents.platform_agents.instagram_agent import InstagramAgent
from app.agents.platform_agents.youtube_agent import YouTubeAgent
from app.agents.platform_agents.school_agent import SchoolAgent


class TestLinkedInAgent:
    """Test suite for LinkedInAgent."""
    
    @pytest.mark.asyncio
    async def test_creates_post_with_correct_tone(
        self,
        mock_openai_service,
        sample_conversation_history,
    ):
        """Test that LinkedIn posts have professional tone."""
        mock_response = "Here's a professional LinkedIn post about AI automation..."
        mock_openai_service.complete = AsyncMock(return_value=mock_response)
        
        with patch(
            "app.agents.platform_agents.linkedin_agent.OpenAIService",
            return_value=mock_openai_service,
        ):
            agent = LinkedInAgent()
            post = await agent.create_post(
                "Create a post about AI",
                sample_conversation_history,
            )
            
            assert post == mock_response
            mock_openai_service.complete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handles_api_failure(self, mock_openai_service, sample_conversation_history):
        """Test error handling when OpenAI API fails."""
        mock_openai_service.complete = AsyncMock(side_effect=Exception("API Error"))
        
        with patch(
            "app.agents.platform_agents.linkedin_agent.OpenAIService",
            return_value=mock_openai_service,
        ):
            agent = LinkedInAgent()
            
            with pytest.raises(Exception):
                await agent.create_post("Create a post", sample_conversation_history)


class TestXAgent:
    """Test suite for XAgent."""
    
    @pytest.mark.asyncio
    async def test_respects_character_limits(
        self,
        mock_openai_service,
        sample_conversation_history,
    ):
        """Test that X posts are under 280 characters."""
        mock_response = "A" * 300  # Intentionally too long
        mock_openai_service.complete = AsyncMock(return_value=mock_response)
        
        with patch(
            "app.agents.platform_agents.x_agent.OpenAIService",
            return_value=mock_openai_service,
        ):
            agent = XAgent()
            post = await agent.create_post(
                "Create a tweet",
                sample_conversation_history,
            )
            
            assert len(post) <= 280
    
    @pytest.mark.asyncio
    async def test_creates_concise_post(
        self,
        mock_openai_service,
        sample_conversation_history,
    ):
        """Test that X posts are concise."""
        mock_response = "AI automation is transforming how we work. #AI #Automation"
        mock_openai_service.complete = AsyncMock(return_value=mock_response)
        
        with patch(
            "app.agents.platform_agents.x_agent.OpenAIService",
            return_value=mock_openai_service,
        ):
            agent = XAgent()
            post = await agent.create_post(
                "Create a tweet about AI",
                sample_conversation_history,
            )
            
            assert post == mock_response
            assert len(post) <= 280


class TestInstagramAgent:
    """Test suite for InstagramAgent."""
    
    @pytest.mark.asyncio
    async def test_creates_visual_caption(
        self,
        mock_openai_service,
        sample_conversation_history,
    ):
        """Test that Instagram captions are visual-focused."""
        mock_response = "✨ Amazing sunset vibes 🌅\n\n#sunset #travel"
        mock_openai_service.complete = AsyncMock(return_value=mock_response)
        
        with patch(
            "app.agents.platform_agents.instagram_agent.OpenAIService",
            return_value=mock_openai_service,
        ):
            agent = InstagramAgent()
            post = await agent.create_post(
                "Create a caption about sunset",
                sample_conversation_history,
            )
            
            assert post == mock_response


class TestYouTubeAgent:
    """Test suite for YouTubeAgent."""
    
    @pytest.mark.asyncio
    async def test_creates_title_and_description(
        self,
        mock_openai_service,
        sample_conversation_history,
    ):
        """Test that YouTube content includes title and description."""
        mock_response = "**Title:** Amazing Python Tutorial\n\n**Description:** Learn Python..."
        mock_openai_service.complete = AsyncMock(return_value=mock_response)
        
        with patch(
            "app.agents.platform_agents.youtube_agent.OpenAIService",
            return_value=mock_openai_service,
        ):
            agent = YouTubeAgent()
            content = await agent.create_post(
                "Create YouTube content for Python tutorial",
                sample_conversation_history,
            )
            
            assert "Title" in content
            assert "Description" in content


class TestSchoolAgent:
    """Test suite for SchoolAgent."""
    
    @pytest.mark.asyncio
    async def test_creates_community_post(
        self,
        mock_openai_service,
        sample_conversation_history,
    ):
        """Test that School posts are community-focused."""
        mock_response = "Hey everyone! Let's discuss AI automation."
        mock_openai_service.complete = AsyncMock(return_value=mock_response)
        
        with patch(
            "app.agents.platform_agents.school_agent.OpenAIService",
            return_value=mock_openai_service,
        ):
            agent = SchoolAgent()
            post = await agent.create_post(
                "Create a post about AI",
                sample_conversation_history,
            )
            
            # Should add signature if not present
            assert "Love an automation" in post
