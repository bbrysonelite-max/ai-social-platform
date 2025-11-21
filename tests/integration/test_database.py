"""
Integration tests for database operations.
"""

import pytest
from app.models.database import Conversation, Message, ImageVersion, GeneratedPost


class TestDatabaseOperations:
    """Test suite for database operations."""
    
    def test_create_conversation(self, test_db_manager):
        """Test creating a conversation."""
        session = test_db_manager.get_session()
        
        conversation = Conversation(
            telegram_user_id=123456,
            telegram_chat_id=789012,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        assert conversation.id is not None
        assert conversation.telegram_user_id == 123456
        assert conversation.telegram_chat_id == 789012
        assert conversation.created_at is not None
        
        session.close()
    
    def test_save_message(self, test_db_manager):
        """Test saving a message."""
        session = test_db_manager.get_session()
        
        # Create conversation first
        conversation = Conversation(
            telegram_user_id=123456,
            telegram_chat_id=789012,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        # Create message
        message = Message(
            conversation_id=conversation.id,
            role="user",
            content="Hello, world!",
            message_type="text",
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.role == "user"
        assert message.content == "Hello, world!"
        assert message.created_at is not None
        
        session.close()
    
    def test_retrieve_conversation_history(self, test_db_manager):
        """Test retrieving conversation history."""
        session = test_db_manager.get_session()
        
        # Create conversation
        conversation = Conversation(
            telegram_user_id=123456,
            telegram_chat_id=789012,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        # Add multiple messages
        messages_data = [
            ("user", "Hello"),
            ("assistant", "Hi there!"),
            ("user", "Create a post"),
        ]
        
        for role, content in messages_data:
            message = Message(
                conversation_id=conversation.id,
                role=role,
                content=content,
                message_type="text",
            )
            session.add(message)
        
        session.commit()
        
        # Retrieve messages
        retrieved_messages = (
            session.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
            .all()
        )
        
        assert len(retrieved_messages) == 3
        assert retrieved_messages[0].content == "Hello"
        assert retrieved_messages[1].content == "Hi there!"
        assert retrieved_messages[2].content == "Create a post"
        
        session.close()
    
    def test_save_image_version(self, test_db_manager):
        """Test saving an image version."""
        session = test_db_manager.get_session()
        
        # Create conversation
        conversation = Conversation(
            telegram_user_id=123456,
            telegram_chat_id=789012,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        # Create image version
        image_version = ImageVersion(
            conversation_id=conversation.id,
            original_image_id="original_123",
            drive_file_id="drive_456",
            drive_file_name="test_image.jpg",
            imagebb_url="https://imagebb.com/test.jpg",
            replicate_output_url="https://replicate.com/output.jpg",
            edit_instruction="Change text to Hello",
            version_number=1,
        )
        session.add(image_version)
        session.commit()
        session.refresh(image_version)
        
        assert image_version.id is not None
        assert image_version.conversation_id == conversation.id
        assert image_version.version_number == 1
        assert image_version.edit_instruction == "Change text to Hello"
        
        session.close()
    
    def test_cascade_delete(self, test_db_manager):
        """Test that deleting a conversation cascades to related records."""
        session = test_db_manager.get_session()
        
        # Create conversation with messages
        conversation = Conversation(
            telegram_user_id=123456,
            telegram_chat_id=789012,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        message = Message(
            conversation_id=conversation.id,
            role="user",
            content="Test message",
            message_type="text",
        )
        session.add(message)
        session.commit()
        
        conversation_id = conversation.id
        
        # Delete conversation
        session.delete(conversation)
        session.commit()
        
        # Verify messages are also deleted
        remaining_messages = (
            session.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .all()
        )
        
        assert len(remaining_messages) == 0
        
        session.close()
    
    def test_save_generated_post(self, test_db_manager):
        """Test saving a generated post."""
        session = test_db_manager.get_session()
        
        # Create conversation
        conversation = Conversation(
            telegram_user_id=123456,
            telegram_chat_id=789012,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        # Create generated post
        post = GeneratedPost(
            conversation_id=conversation.id,
            platform="linkedin",
            content="This is a LinkedIn post about AI automation.",
            prompt="Create a LinkedIn post about AI",
        )
        session.add(post)
        session.commit()
        session.refresh(post)
        
        assert post.id is not None
        assert post.platform == "linkedin"
        assert "AI automation" in post.content
        
        session.close()
