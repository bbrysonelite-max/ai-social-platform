# Test Specifications

## AI Social Media Automation System

**Version:** 1.0  
**Date:** 2025-11-19

---

### 1. Testing Philosophy

The testing strategy for this system is built on the following principles:

- **Test-First Mindset**: Tests define the contract. If it's not tested, it doesn't exist.
- **Isolation**: Unit tests must be fully isolated with no external dependencies.
- **Coverage**: 100% coverage of business logic. Infrastructure code (e.g., FastAPI routes) may have lower coverage.
- **Speed**: Unit tests must run in under 5 seconds total. Integration tests under 30 seconds.
- **Clarity**: Test names must describe the exact scenario being tested.

### 2. Test Structure

```
tests/
├── unit/                      # Fast, isolated tests
│   ├── test_super_agent.py
│   ├── test_post_creator.py
│   ├── test_platform_agents.py
│   ├── test_image_improver.py
│   └── test_services.py
├── integration/               # Tests with real database
│   ├── test_telegram_flow.py
│   ├── test_database.py
│   └── test_agent_integration.py
└── conftest.py               # Shared fixtures
```

### 3. Unit Test Specifications

#### 3.1. Super Agent Tests (`test_super_agent.py`)

**Test Class**: `TestSuperAgent`

| Test Name | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| `test_process_text_routes_to_post_creator` | User sends "Create a LinkedIn post" | Intent detected as `CREATE_POST`, routed to `PostCreatorAgent` |
| `test_process_text_routes_to_general` | User sends "Hello" | Intent detected as `GENERAL`, handled by general conversation |
| `test_process_image_with_edit_instruction` | User uploads image with "Change text to Hello" | Intent detected as `EDIT_ONLY`, routed to `ImageImproverAgent` |
| `test_process_image_with_post_request` | User uploads image with "Create a LinkedIn post" | Intent detected as `POST_ONLY`, routed to `PostCreatorAgent` |
| `test_process_image_with_both_intents` | User uploads image with "Edit and create post" | Intent detected as `BOTH`, both agents invoked |
| `test_conversation_history_retrieved` | Any request | Conversation history fetched from database |
| `test_response_saved_to_database` | Any successful request | Assistant response persisted to `messages` table |
| `test_handles_llm_failure_gracefully` | OpenAI API fails | Returns user-friendly error message, no crash |

**Mocks Required**: `OpenAI`, `PostCreatorAgent`, `ImageImproverAgent`, Database

#### 3.2. Post Creator Tests (`test_post_creator.py`)

**Test Class**: `TestPostCreatorAgent`

| Test Name | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| `test_detect_single_platform` | Prompt mentions "LinkedIn" | Returns `[Platform.LINKEDIN]` |
| `test_detect_multiple_platforms` | Prompt mentions "X and Instagram" | Returns `[Platform.X, Platform.INSTAGRAM]` |
| `test_detect_no_platform` | Prompt is generic | Returns empty list |
| `test_parallel_post_generation` | Request for 3 platforms | All 3 platform agents invoked concurrently |
| `test_handles_platform_agent_failure` | One platform agent fails | Other platforms succeed, error reported for failed one |
| `test_formats_response_correctly` | Multiple posts generated | Response formatted with platform headers |

**Mocks Required**: `OpenAI`, all `PlatformAgent` classes

#### 3.3. Platform Agent Tests (`test_platform_agents.py`)

**Test Classes**: `TestLinkedInAgent`, `TestXAgent`, `TestInstagramAgent`, `TestYouTubeAgent`, `TestSchoolAgent`

| Test Name | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| `test_creates_post_with_correct_tone` | Valid prompt | Post matches platform-specific tone and format |
| `test_respects_character_limits` | Long prompt (X only) | Post is under 280 characters |
| `test_includes_hashtags` | Valid prompt | Post includes appropriate hashtags |
| `test_handles_api_failure` | OpenAI API fails | Raises exception with clear error message |
| `test_uses_conversation_history` | Prompt with history | History included in API call for context |

**Mocks Required**: `OpenAI`

#### 3.4. Image Improver Tests (`test_image_improver.py`)

**Test Class**: `TestImageImproverAgent`

| Test Name | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| `test_full_workflow_success` | Valid image and instructions | All steps execute, URL returned |
| `test_version_number_increments` | Second edit in conversation | Version number is 2 |
| `test_saves_to_database` | Successful edit | `ImageVersion` record created |
| `test_handles_drive_upload_failure` | Google Drive fails | Returns error message, no crash |
| `test_handles_replicate_failure` | Replicate API fails | Returns error message, no crash |
| `test_handles_imagebb_failure` | imageBB fails | Returns error message, no crash |

**Mocks Required**: `GoogleDriveService`, `ImageBBService`, `ReplicateService`, Database

#### 3.5. Service Tests (`test_services.py`)

**Test Classes**: `TestGoogleDriveService`, `TestImageBBService`, `TestReplicateService`

| Test Name | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| `test_upload_image_success` | Valid image file | Returns file ID |
| `test_upload_image_invalid_credentials` | Invalid API key | Raises exception |
| `test_download_image_success` | Valid file ID | Downloads file to specified path |
| `test_api_call_timeout` | API takes too long | Raises timeout exception |
| `test_handles_network_error` | Network failure | Raises connection exception |

**Mocks Required**: External API responses (using `httpx` mock or `responses` library)

### 4. Integration Test Specifications

#### 4.1. Telegram Flow Tests (`test_telegram_flow.py`)

**Test Class**: `TestTelegramIntegration`

| Test Name | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| `test_start_command` | User sends `/start` | Welcome message returned |
| `test_unauthorized_user_blocked` | Non-whitelisted user sends message | Access denied message |
| `test_text_message_end_to_end` | User sends "Create a LinkedIn post" | Post generated and returned |
| `test_image_message_end_to_end` | User uploads image with caption | Image processed and result returned |

**Mocks Required**: External APIs (OpenAI, Replicate, etc.), Telegram API responses

#### 4.2. Database Tests (`test_database.py`)

**Test Class**: `TestDatabaseOperations`

| Test Name | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| `test_create_conversation` | New user starts conversation | `Conversation` record created |
| `test_save_message` | Message sent | `Message` record created with correct fields |
| `test_retrieve_conversation_history` | Multiple messages exist | Messages returned in chronological order |
| `test_save_image_version` | Image edited | `ImageVersion` record created |
| `test_cascade_delete` | Conversation deleted | All related messages and image versions deleted |

**Database**: Real test database (SQLite in-memory or separate test PostgreSQL)

#### 4.3. Agent Integration Tests (`test_agent_integration.py`)

**Test Class**: `TestAgentIntegration`

| Test Name | Scenario | Expected Behavior |
|-----------|----------|-------------------|
| `test_super_agent_to_post_creator` | Full flow from SuperAgent to PostCreator | Correct routing and response |
| `test_super_agent_to_image_improver` | Full flow from SuperAgent to ImageImprover | Correct routing and response |
| `test_parallel_platform_agents` | PostCreator invokes multiple agents | All agents execute concurrently |

**Mocks Required**: External APIs only

### 5. Test Fixtures (`conftest.py`)

**Required Fixtures**:

- `mock_openai_client`: Mocked OpenAI client with predefined responses
- `mock_replicate_client`: Mocked Replicate client
- `mock_google_drive_service`: Mocked Google Drive service
- `mock_imagebb_service`: Mocked imageBB service
- `test_db`: In-memory SQLite database for integration tests
- `sample_conversation`: Pre-populated conversation with history
- `sample_image_path`: Path to a test image file

### 6. Test Data

**Sample Prompts**:
- `"Create a LinkedIn post about AI automation"`
- `"Make posts for X and Instagram about productivity"`
- `"Write a YouTube description for a video about Python"`

**Sample Image Instructions**:
- `"Change the text to Hello World"`
- `"Make the background blue"`
- `"Add a logo in the top right corner"`

**Sample Conversation History**:
```python
[
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help you today?"},
    {"role": "user", "content": "Create a LinkedIn post about AI"}
]
```

### 7. Coverage Requirements

- **Unit Tests**: 100% coverage of all business logic in `app/agents/` and `app/services/`
- **Integration Tests**: 80% coverage of `app/telegram/` and database operations
- **Overall**: Minimum 90% total coverage

### 8. Performance Requirements

- **Unit Tests**: Total execution time < 5 seconds
- **Integration Tests**: Total execution time < 30 seconds
- **Individual Test**: No single test should take > 2 seconds

### 9. Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_super_agent.py

# Run specific test
pytest tests/unit/test_super_agent.py::TestSuperAgent::test_process_text_routes_to_post_creator
```

### 10. Continuous Integration

- Tests must pass before any code is merged
- Coverage must not decrease
- All tests must be deterministic (no flaky tests)

---

This test specification ensures comprehensive coverage and maintains the quality bar for the AI Social Media Automation System.
