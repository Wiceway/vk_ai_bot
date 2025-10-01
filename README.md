# VK AI Bot

AI-powered chatbot for VK (VKontakte) conversations. The bot can be added to group conversations and configured to respond with AI-generated messages based on customizable personality, role, and behavior settings.

## Features

- 🤖 **AI-powered responses** using OpenAI GPT models
- 👥 **Admin management** - control who can configure the bot
- 🎭 **Customizable personality** - set role and task for the bot
- 📏 **Adjustable response length** - short, medium, or long responses
- 🎯 **User targeting** - respond only to specific users
- 📊 **Response percentage** - control how often the bot responds (1-100%)
- 🧠 **Conversation memory** - configurable history size for context
- 💾 **Persistent storage** - SQLite database for configuration and history

## Requirements

- Python 3.10+
- VK Community with Bot API access
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Wiceway/vk_ai_bot.git
cd vk_ai_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your tokens:
```env
VK_TOKEN=your_vk_group_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### Getting VK Token

1. Go to your VK community: https://vk.com/groups?tab=admin
2. Select your community → Settings → API usage → Access tokens
3. Create a new token with permissions: "messages" and "group messages"
4. Copy the token to `.env`

### Getting OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key to `.env`

## Usage

### Starting the Bot

```bash
python main.py
```

The bot will start and listen for messages in conversations where it's added.

### Adding Bot to Conversation

1. Add your VK community to the conversation
2. The first person who sends a command becomes the first admin
3. Configure the bot using admin commands

## Admin Commands

### General Commands
- `!помощь` or `!help` - Show help message
- `!команды` - Show available commands
- `!статус` - Show current bot configuration

### Admin Management
- `!добавить_админа [id]` - Add administrator
- `!удалить_админа [id]` - Remove administrator
- `!список_админов` - List all admins

**Example:**
```
!добавить_админа 123456789
!добавить_админа @username
!добавить_админа [id123456789|@username]
```

### Brain Configuration
- `!установить_роль [text]` - Set bot's role/personality
- `!установить_задачу [text]` - Set bot's task/purpose
- `!установить_мозги [role] | [task]` - Set role and task in one command

**Example:**
```
!установить_роль Я водитель грузовика с 20-летним стажем вождения
!установить_задачу Я пишу в этом чате, чтобы скоротать время за рулем
```

Or combined:
```
!установить_мозги Я водитель грузовика | Скоротать время за рулем
```

### Response Settings
- `!длина_ответов [short/medium/long]` - Set response length
- `!процент_ответов [1-100]` - Set response percentage
- `!размер_памяти [number]` - Set memory size (number of messages to remember)

**Example:**
```
!длина_ответов medium
!процент_ответов 50
!размер_памяти 20
```

### User Management
- `!добавить_пользователя [id]` - Add user to tracking list
- `!удалить_пользователя [id]` - Remove user from tracking list
- `!список_пользователей` - List tracked users

**Example:**
```
!добавить_пользователя 123456789
!добавить_пользователя @username
```

**Note:** The bot will only respond to messages from users in the tracking list!

## Configuration

### Response Length Options

- **short** - Very brief, 1-2 sentences max
- **medium** - Medium length, 2-4 sentences (default)
- **long** - Detailed responses, multiple sentences

### Response Percentage

Controls how often the bot responds to tracked users' messages:
- **100%** - Respond to every message (default)
- **50%** - Respond to approximately half of messages
- **25%** - Respond to approximately 1 in 4 messages

This creates more natural conversation flow by not responding to every single message.

### Memory Size

Number of previous messages the bot remembers for context:
- **Default:** 10 messages
- **Recommended:** 10-30 messages
- Higher values provide more context but use more AI tokens

## Project Structure

```
vk_ai_bot/
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore file
├── requirements.txt     # Python dependencies
├── main.py             # Entry point
├── README.md           # This file
├── bot/
│   ├── __init__.py
│   ├── ai.py           # AI integration (OpenAI)
│   ├── handlers.py     # Message handlers
│   └── admin.py        # Admin commands
├── database/
│   ├── __init__.py
│   └── db.py           # Database operations
└── config/
    ├── __init__.py
    └── config.py       # Configuration management
```

## Database Schema

The bot uses SQLite database with three main tables:

- **conversations** - Bot configuration per conversation
- **tracked_users** - Users whose messages trigger bot responses
- **conversation_history** - Message history for context

## Troubleshooting

### Bot doesn't respond to messages

1. Make sure you've added users to the tracking list:
   ```
   !добавить_пользователя [user_id]
   ```

2. Check the response percentage:
   ```
   !статус
   ```

3. Verify the bot has messages enabled in VK community settings

### "Configuration error" on startup

Make sure your `.env` file contains valid tokens:
- `VK_TOKEN` - from VK community settings
- `OPENAI_API_KEY` - from OpenAI platform

### Bot responds but messages are generic

Configure the bot's personality:
```
!установить_роль [describe the character]
!установить_задачу [describe the purpose]
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open source and available for use.

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing issues for solutions

## Related Links

- [VK API Documentation](https://dev.vk.com/api/bots)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [vkbottle Documentation](https://github.com/vkbottle/vkbottle)
