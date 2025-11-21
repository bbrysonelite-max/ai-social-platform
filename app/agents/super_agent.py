"""
Super Agent - Main orchestrator for the AI Social Media System.

Handles intent analysis, routing, and coordination between sub-agents.
"""

import logging
from app.types import MessageDict, ConversationID
from app.models.database import DatabaseManager, Message
from app.services.openai_service import OpenAIService
from app.agents.post_creator import PostCreatorAgent
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SuperAgent:
    """
    Central orchestrator for all user requests.
    
    Responsibilities:
    - Analyze user intent
    - Route to appropriate sub-agent
    - Manage conversation context
    - Format and return responses
    """
    
    def __init__(self, conversation_id: ConversationID, db_manager: DatabaseManager):
        """
        Initialize Super Agent.
        
        Args:
            conversation_id: ID of the current conversation
            db_manager: Database manager instance
        """
        self.conversation_id = conversation_id
        self.db_manager = db_manager
        self.openai = OpenAIService()
        self.post_creator = PostCreatorAgent()
    
    async def process_text(self, text: str) -> str:
        """
        Process a text-only message.
        
        Args:
            text: User's text input
            
        Returns:
            Response text
        """
        logger.info(f"SuperAgent processing text for conversation {self.conversation_id}")
        
        # Get conversation history
        history = self._get_conversation_history()
        
        # Analyze intent
        intent = await self.openai.analyze_intent(text, history)
        logger.info(f"Detected intent: {intent}")
        
        # Route based on intent
        if intent == "create_post":
            return await self.post_creator.create_posts(text, history)
        elif intent == "edit_image":
            return self._image_upload_required_response()
        else:
            return await self._handle_general_conversation(text, history)
    
    async def process_image(self, image_path: str, caption: str) -> str:
        """
        Process an image with optional caption.
        
        Args:
            image_path: Path to the downloaded image
            caption: User's caption/instructions
            
        Returns:
            Response text
        """
        logger.info(f"SuperAgent processing image for conversation {self.conversation_id}")
        
        if not caption:
            return self._image_instructions_required_response()
        
        # Get conversation history
        history = self._get_conversation_history()
        
        # Analyze image intent
        intent = await self.openai.analyze_image_intent(caption)
        logger.info(f"Detected image intent: {intent}")
        
        if intent == "edit_only":
            # Image editing not implemented in this phase
            return self._image_editing_not_available_response()
        elif intent == "post_only":
            context = f"User uploaded an image and wants: {caption}"
            return await self.post_creator.create_posts(context, history)
        else:  # "both"
            return self._image_editing_not_available_response()
    
    def _get_conversation_history(
        self,
        limit: int | None = None,
    ) -> list[MessageDict]:
        """
        Get recent conversation history.
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages in chronological order
        """
        if limit is None:
            limit = settings.MAX_CONVERSATION_HISTORY
        
        session = self.db_manager.get_session()
        try:
            messages = (
                session.query(Message)
                .filter(Message.conversation_id == self.conversation_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
                .all()
            )
            
            # Reverse to get chronological order
            history: list[MessageDict] = [
                {"role": msg.role, "content": msg.content}  # type: ignore
                for msg in reversed(messages)
            ]
            
            return history
            
        finally:
            session.close()
    
    async def _handle_general_conversation(
        self,
        text: str,
        history: list[MessageDict],
    ) -> str:
        """Handle general conversation."""
        system_prompt = """You are a helpful AI assistant for a social media automation system.

You help users create social media content and edit images. Be friendly and guide them
on how to use the system effectively.

Your capabilities:
- Create posts for X (Twitter), LinkedIn, Instagram, YouTube, and School
- Edit images with AI (coming soon)
- Generate multi-platform content simultaneously

Keep responses concise and helpful."""
        
        messages: list[MessageDict] = [
            {"role": "system", "content": system_prompt},
            *history[-5:],
            {"role": "user", "content": text},
        ]
        
        try:
            return await self.openai.complete(messages, temperature=0.7, max_tokens=500)
        except Exception as e:
            logger.error(f"Error in general conversation: {e}")
            return "I'm sorry, I encountered an error. Please try again."
    
    def _image_upload_required_response(self) -> str:
        """Response when user wants to edit image but hasn't uploaded one."""
        return (
            "📸 To edit an image, please upload an image along with your instructions.\n\n"
            "For example, upload a photo and add a caption like:\n"
            "• 'Change the text to Hello World'\n"
            "• 'Make the background blue'\n"
            "• 'Add a second dog to this image'"
        )
    
    def _image_instructions_required_response(self) -> str:
        """Response when image uploaded without instructions."""
        return (
            "📸 I received your image! What would you like me to do with it?\n\n"
            "You can:\n"
            "• Edit the image: 'Change the text to...', 'Make the background blue'\n"
            "• Create a post: 'Write a LinkedIn post about this image'\n"
            "• Both: 'Add a logo and create an Instagram post'"
        )
    
    def _image_editing_not_available_response(self) -> str:
        """Response when image editing is requested but not configured."""
        return (
            "🎨 Image editing requires additional configuration.\n\n"
            "To enable image editing, please configure:\n"
            "• IMAGEBB_API_KEY\n"
            "• REPLICATE_API_TOKEN\n\n"
            "I can still help you create posts about your image!"
        )
