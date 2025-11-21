"""
Unit tests for Post Creator Agent.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.agents.post_creator import PostCreatorAgent


class TestPostCreatorAgent:
    """Test suite for PostCreatorAgent."""
    
    @pytest.mark.asyncio
    async def test_detect_single_platform(
        self,
        mock_openai_service,
        sample_conversation_history,
    ):
        """Test detection of a single platform."""
        mock_openai_service.detect_platforms = AsyncMock(return_value=["linkedin"])
        
        with patch("app.agents.post_creator.OpenAIService", return_value=mock_openai_service):
            with patch("app.agents.post_creator.LinkedInAgent") as mock_linkedin:
                mock_linkedin_instance = AsyncMock()
                mock_linkedin_instance.create_post = AsyncMock(
                    return_value="LinkedIn post content"
                )
                mock_linkedin.return_value = mock_linkedin_instance
                
                agent = PostCreatorAgent()
                response = await agent.create_posts(
                    "Create a LinkedIn post",
                    sample_conversation_history,
                )
                
                assert "LinkedIn" in response
                assert "LinkedIn post content" in response
                mock_linkedin_instance.create_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_detect_multiple_platforms(
        self,
        mock_openai_service,
        sample_conversation_history,
    ):
        """Test detection of multiple platforms."""
        mock_openai_service.detect_platforms = AsyncMock(return_value=["x", "linkedin"])
        
        with patch("app.agents.post_creator.OpenAIService", return_value=mock_openai_service):
            with patch("app.agents.post_creator.XAgent") as mock_x:
                with patch("app.agents.post_creator.LinkedInAgent") as mock_linkedin:
                    mock_x_instance = AsyncMock()
                    mock_x_instance.create_post = AsyncMock(return_value="X post")
                    mock_x.return_value = mock_x_instance
                    
                    mock_linkedin_instance = AsyncMock()
                    mock_linkedin_instance.create_post = AsyncMock(
                        return_value="LinkedIn post"
                    )
                    mock_linkedin.return_value = mock_linkedin_instance
                    
                    agent = PostCreatorAgent()
                    response = await agent.create_posts(
                        "Create posts for X and LinkedIn",
                        sample_conversation_history,
                    )
                    
                    assert "X" in response
                    assert "LinkedIn" in response
                    mock_x_instance.create_post.assert_called_once()
                    mock_linkedin_instance.create_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_detect_no_platform(
        self,
        mock_openai_service,
        sample_conversation_history,
    ):
        """Test handling when no platform is detected."""
        mock_openai_service.detect_platforms = AsyncMock(return_value=[])
        
        with patch("app.agents.post_creator.OpenAIService", return_value=mock_openai_service):
            agent = PostCreatorAgent()
            response = await agent.create_posts(
                "Hello",
                sample_conversation_history,
            )
            
            assert "platform" in response.lower()
            assert "X" in response or "LinkedIn" in response
    
    @pytest.mark.asyncio
    async def test_handles_platform_agent_failure(
        self,
        mock_openai_service,
        sample_conversation_history,
    ):
        """Test handling when a platform agent fails."""
        mock_openai_service.detect_platforms = AsyncMock(return_value=["linkedin"])
        
        with patch("app.agents.post_creator.OpenAIService", return_value=mock_openai_service):
            with patch("app.agents.post_creator.LinkedInAgent") as mock_linkedin:
                mock_linkedin_instance = AsyncMock()
                mock_linkedin_instance.create_post = AsyncMock(
                    side_effect=Exception("API Error")
                )
                mock_linkedin.return_value = mock_linkedin_instance
                
                agent = PostCreatorAgent()
                response = await agent.create_posts(
                    "Create a LinkedIn post",
                    sample_conversation_history,
                )
                
                # Should still return a response with error indication
                assert "linkedin" in response.lower()
                assert "❌" in response or "Error" in response
