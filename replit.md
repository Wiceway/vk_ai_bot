# VK AI Bot - Replit Project Documentation

## Overview
This is a VK (VKontakte) chatbot powered by OpenAI's GPT models. The bot can be added to VK group conversations and will respond to messages with AI-generated content based on configurable personality settings, response patterns, and tracked users.

**Current Status**: Project successfully set up and running in Replit environment. Bot requires valid API credentials and VK Long Poll configuration to operate.

## Recent Changes

### October 1, 2025 - Initial Replit Setup
- Installed Python 3.11 and all required dependencies
- Fixed httpx compatibility issue (pinned to 0.27.2 for openai 1.54.0 compatibility)
- Fixed type hint issue in bot/ai.py (changed `any` to `Any`)
- Added type assertions in main.py for better type safety
- Created .env file from template
- Configured workflow to run bot with console output
- Database initialization working correctly (SQLite with aiosqlite)

## Project Architecture

### Core Technologies
- **Language**: Python 3.11
- **VK Integration**: vkbottle 4.3.12
- **AI Provider**: OpenAI API (openai 1.54.0)
- **Database**: SQLite with aiosqlite 0.19.0
- **Configuration**: python-dotenv 1.0.0

### Directory Structure
```
vk_ai_bot/
├── bot/
│   ├── ai.py           # OpenAI integration and response generation
│   ├── handlers.py     # Message handlers and bot logic
│   └── admin.py        # Admin commands (Russian language)
├── config/
│   └── config.py       # Configuration management and validation
├── database/
│   └── db.py           # Database operations (conversations, users, history)
├── main.py             # Entry point
├── requirements.txt    # Python dependencies
└── .env                # Environment variables (not in git)
```

### Database Schema
Three main tables managed by SQLite:
1. **conversations**: Bot configuration per VK conversation (admins, brain settings, response config)
2. **tracked_users**: Users whose messages trigger bot responses
3. **conversation_history**: Message history for AI context

## Required Configuration

### Environment Variables (in Replit Secrets or .env)
- `VK_TOKEN`: VK community access token (required)
  - Get from: VK community → Settings → API usage → Access tokens
  - Needs permissions: "messages" and "group messages"
  
- `OPENAI_API_KEY`: OpenAI API key (required)
  - Get from: https://platform.openai.com/api-keys
  
- `OPENAI_MODEL`: OpenAI model to use (optional, defaults to gpt-3.5-turbo)

### VK Community Setup
**Important**: The VK community must have **Long Poll API enabled**:
1. Go to VK community → Settings → API usage → Long Poll API
2. Enable Long Poll API
3. Set API version to 5.131 or higher
4. Enable "Message new" event type

Without Long Poll enabled, the bot will fail with: "longpoll for this group is not enabled"

## How It Works

### Bot Flow
1. Bot connects to VK using Long Poll API
2. Listens for new messages in conversations where it's added
3. First user to send a command becomes the first admin
4. Admins configure bot personality (role, task) and settings
5. Admins add users to tracking list
6. Bot responds to tracked users' messages based on:
   - Configured personality/role
   - Response percentage (1-100%)
   - Response length (short/medium/long)
   - Conversation history (configurable memory size)

### Admin Commands (Russian)
All commands start with `!`:
- `!помощь` / `!help` - Show help
- `!статус` - Show current configuration
- `!установить_роль [text]` - Set bot personality
- `!установить_задачу [text]` - Set bot purpose
- `!добавить_пользователя [id]` - Add user to tracking
- `!процент_ответов [1-100]` - Set response frequency
- `!длина_ответов [short/medium/long]` - Set response length
- `!размер_памяти [number]` - Set conversation memory size

See README.md for complete command reference.

## Known Issues & Solutions

### httpx Version Compatibility
**Issue**: OpenAI 1.54.0 incompatible with httpx 0.28.0+  
**Solution**: Pinned httpx==0.27.2 in requirements.txt  
**Status**: Fixed

### Type Hint Errors
**Issue**: LSP showing import errors after package installation  
**Solution**: These are false positives; imports work correctly at runtime  
**Status**: Cosmetic only, no impact on functionality

## Workflow Configuration

**Name**: Bot  
**Command**: `python main.py`  
**Output Type**: console (backend service)  
**Port**: N/A (no web server, polls VK API)

The workflow automatically restarts when dependencies change.

## User Preferences
None documented yet.

## Development Notes

### Testing the Bot
1. Ensure VK_TOKEN and OPENAI_API_KEY are set in Replit Secrets
2. Verify VK community has Long Poll API enabled
3. Check workflow console for successful startup message: "Starting polling for..."
4. Add bot to a VK conversation
5. Send `!помощь` to see commands
6. Add yourself to tracked users with `!добавить_пользователя [your_id]`
7. Configure bot personality and start chatting

### Database
SQLite database file (`bot_data.db`) is automatically created on first run and is excluded from git (.gitignore).

### Logs
Bot uses Python's logging module (INFO level). Consider migrating to loguru as recommended by vkbottle.
