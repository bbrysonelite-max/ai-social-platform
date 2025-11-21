# AI Social Media Automation System

A production-grade, self-hosted AI system for automating social media content creation through a Telegram interface. Built with clean architecture, strict type safety, and comprehensive testing.

## Features

- **Multi-Platform Content Generation**: Create optimized posts for X (Twitter), LinkedIn, Instagram, YouTube, and School
- **Intelligent Routing**: AI-powered intent analysis automatically routes requests to the appropriate agent
- **Parallel Processing**: Generate content for multiple platforms simultaneously
- **Conversation Context**: Maintains conversation history for contextual responses
- **Type-Safe**: Strict typing throughout with Pydantic validation
- **Fully Tested**: Comprehensive unit and integration test suite
- **Production-Ready**: Clean architecture, proper error handling, and logging

## Architecture

```
User → Telegram Bot → Super Agent → Post Creator → Platform Agents
                           ↓              ↓
                      Database    OpenAI API
```

### Components

- **Super Agent**: Central orchestrator for intent analysis and routing
- **Post Creator**: Manages multi-platform content generation
- **Platform Agents**: Specialized agents for each social media platform
- **Database**: SQLAlchemy ORM with conversation and message tracking
- **Telegram Bot**: User interface via Telegram

## Requirements

- Python 3.11+
- OpenAI API key
- Telegram Bot Token
- SQLite (default) or PostgreSQL

## Quick Start

### 1. Clone and Install

```bash
git clone <repository-url>
cd ai-social-system
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set required variables:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321  # Optional: comma-separated user IDs
```

### 3. Run the Application

```bash
python -m app.main
```

The bot will start polling for messages. Send `/start` to your bot on Telegram to begin.

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot API token | `123456:ABC-DEF...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_ALLOWED_USER_IDS` | Comma-separated user IDs for whitelist | Empty (all users allowed) |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4-turbo-preview` |
| `OPENAI_TEMPERATURE` | Sampling temperature | `0.7` |
| `DATABASE_URL` | Database connection string | `sqlite:///./ai_social_system.db` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG` | Enable debug mode | `False` |

## Usage

### Creating Posts

Send a message to your bot:

```
Create a LinkedIn post about AI automation
```

The system will:
1. Analyze your intent
2. Detect the target platform(s)
3. Generate platform-optimized content
4. Return the result

### Multi-Platform Posts

```
Create posts for X and LinkedIn about remote work
```

The system generates content for all requested platforms in parallel.

### Supported Platforms

- **X (Twitter)**: Concise, punchy posts under 280 characters
- **LinkedIn**: Professional, thought-leadership content
- **Instagram**: Visual-first captions with emojis and hashtags
- **YouTube**: SEO-optimized titles and descriptions
- **School**: Community-focused educational posts

## Development

### Project Structure

```
ai-social-system/
├── app/
│   ├── agents/              # Agent implementations
│   │   ├── super_agent.py
│   │   ├── post_creator.py
│   │   └── platform_agents/
│   ├── models/              # Database models and schemas
│   ├── services/            # External service integrations
│   ├── telegram/            # Telegram bot implementation
│   ├── config.py            # Configuration management
│   ├── types.py             # Type definitions
│   └── main.py              # Application entry point
├── tests/
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── docker/                  # Docker configuration
├── requirements.txt
├── pytest.ini
├── PDR.md                   # Preliminary Design Review
└── TEST_SPEC.md             # Test specifications
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_super_agent.py
```

### Code Quality

```bash
# Type checking
mypy app/

# Code formatting
black app/ tests/

# Linting
pylint app/
```

## Docker Deployment

### Build Image

```bash
docker build -f docker/Dockerfile -t ai-social-system .
```

### Run Container

```bash
docker run -d \
  --name ai-social-system \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  ai-social-system
```

### Using Docker Compose

```bash
docker-compose -f docker/docker-compose.yml up -d
```

## Production Deployment

### Recommended Setup

1. **Use PostgreSQL** instead of SQLite for production
2. **Set user whitelist** via `TELEGRAM_ALLOWED_USER_IDS`
3. **Enable logging** to file or external service
4. **Set up monitoring** for the `/health` endpoint
5. **Use environment secrets** management (e.g., AWS Secrets Manager)

### Environment Variables for Production

```env
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@localhost/dbname
TELEGRAM_ALLOWED_USER_IDS=123456789
```

### Health Check

The application exposes a health check endpoint:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "telegram_bot": "running",
  "database": "connected"
}
```

## Security

- **User Whitelist**: Restrict access via `TELEGRAM_ALLOWED_USER_IDS`
- **API Keys**: Never commit API keys; use environment variables
- **Input Validation**: All inputs validated via Pydantic
- **Error Handling**: Graceful error handling prevents crashes

## Troubleshooting

### Bot Not Responding

1. Check bot token is correct
2. Verify bot is running: `curl http://localhost:8000/health`
3. Check logs for errors

### Database Errors

1. Ensure database file is writable (SQLite)
2. Check database URL is correct
3. Run migrations if using PostgreSQL

### OpenAI API Errors

1. Verify API key is valid
2. Check API quota and billing
3. Review rate limits

## Contributing

1. Follow the existing code style
2. Write tests for new features
3. Ensure all tests pass: `pytest`
4. Update documentation as needed

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check the PDR.md for technical details
- Review TEST_SPEC.md for testing guidelines

---

**Built with production-grade engineering practices:**
- ✅ Strict type safety
- ✅ Comprehensive testing
- ✅ Clean architecture
- ✅ Proper error handling
- ✅ Zero bloat
