"""
Telegram bot implementation with clean handler architecture.
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from app.types import UserID
from app.config import get_settings
from app.models.database import DatabaseManager, Conversation, Message
from app.agents.super_agent import SuperAgent

logger = logging.getLogger(__name__)
settings = get_settings()


class TelegramBot:
    """Manages Telegram bot lifecycle and message handling."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize Telegram bot.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.application: Application | None = None
    
    async def initialize(self) -> None:
        """Initialize the bot application."""
        logger.info("Initializing Telegram bot...")
        
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(MessageHandler(filters.PHOTO, self._handle_image))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text)
        )
        self.application.add_error_handler(self._error_handler)
        
        logger.info("Telegram bot initialized")
    
    async def start(self) -> None:
        """Start the bot."""
        if not self.application:
            await self.initialize()
        
        logger.info("Starting Telegram bot polling...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
    
    async def stop(self) -> None:
        """Stop the bot."""
        if self.application:
            logger.info("Stopping Telegram bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
    
    def _check_authorization(self, user_id: UserID) -> bool:
        """Check if user is authorized."""
        if not settings.is_user_whitelist_enabled:
            return True
        return user_id in settings.allowed_user_ids
    
    def _get_or_create_conversation(
        self,
        user_id: UserID,
        chat_id: int,
    ) -> Conversation:
        """Get existing conversation or create new one."""
        session = self.db_manager.get_session()
        try:
            conversation = (
                session.query(Conversation)
                .filter(
                    Conversation.telegram_user_id == user_id,
                    Conversation.telegram_chat_id == chat_id,
                )
                .first()
            )
            
            if not conversation:
                conversation = Conversation(
                    telegram_user_id=user_id,
                    telegram_chat_id=chat_id,
                )
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
            
            return conversation
        finally:
            session.close()
    
    def _save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        message_type: str = "text",
    ) -> None:
        """Save a message to the database."""
        session = self.db_manager.get_session()
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                message_type=message_type,
            )
            session.add(message)
            session.commit()
        finally:
            session.close()
    
    async def _start_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle /start command."""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("⛔ You are not authorized to use this bot.")
            return
        
        welcome = (
            "🤖 **AI Social Media System**\n\n"
            "I can help you with:\n"
            "• Generate posts for X, LinkedIn, Instagram, YouTube, and School\n"
            "• Create multi-platform content simultaneously\n\n"
            "Just send me a message to get started!\n\n"
            "Use /help for more information."
        )
        
        await update.message.reply_text(welcome, parse_mode="Markdown")
    
    async def _help_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle /help command."""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("⛔ You are not authorized to use this bot.")
            return
        
        help_text = (
            "📖 **How to Use**\n\n"
            "**Creating Posts:**\n"
            "• Send a text prompt: 'Create a LinkedIn post about AI automation'\n"
            "• Request multiple platforms: 'Make posts for X and Instagram'\n\n"
            "**Tips:**\n"
            "• Be specific with your requests\n"
            "• You can generate content for multiple platforms at once\n"
        )
        
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def _handle_text(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle text messages."""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("⛔ You are not authorized to use this bot.")
            return
        
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        text = update.message.text
        
        logger.info(f"Received text from user {user_id}: {text[:50]}...")
        
        await update.message.chat.send_action("typing")
        
        try:
            # Get or create conversation
            conversation = self._get_or_create_conversation(user_id, chat_id)
            
            # Save user message
            self._save_message(conversation.id, "user", text, "text")
            
            # Process with SuperAgent
            agent = SuperAgent(conversation.id, self.db_manager)
            response = await agent.process_text(text)
            
            # Save assistant response
            self._save_message(conversation.id, "assistant", response, "text")
            
            # Send response
            await update.message.reply_text(response, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error processing text: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Sorry, I encountered an error. Please try again."
            )
    
    async def _handle_image(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle image messages."""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("⛔ You are not authorized to use this bot.")
            return
        
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        caption = update.message.caption or ""
        
        logger.info(f"Received image from user {user_id}")
        
        await update.message.chat.send_action("typing")
        
        try:
            # Download image
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            image_path = f"/tmp/telegram_image_{photo.file_id}.jpg"
            await file.download_to_drive(image_path)
            
            # Get or create conversation
            conversation = self._get_or_create_conversation(user_id, chat_id)
            
            # Save user message
            self._save_message(
                conversation.id,
                "user",
                f"[Image uploaded] {caption}",
                "image",
            )
            
            # Process with SuperAgent
            agent = SuperAgent(conversation.id, self.db_manager)
            response = await agent.process_image(image_path, caption)
            
            # Save assistant response
            self._save_message(conversation.id, "assistant", response, "text")
            
            # Send response
            await update.message.reply_text(response, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error processing image: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Sorry, I encountered an error processing your image."
            )
    
    async def _error_handler(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle errors."""
        logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An unexpected error occurred. Please try again later."
            )
