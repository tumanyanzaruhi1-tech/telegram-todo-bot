# Telegram To-Do Bot

A simple Telegram bot for personal tasks, built with Python, `python-telegram-bot` and SQLite.
Each user sees only their own tasks.

## Commands

| Command | Description |
|---|---|
| `/add <text>` | Add a task |
| `/list` | Show your tasks |
| `/done <id>` | Mark a task as done |
| `/delete <id>` | Delete a task |
| `/clear` | Delete all your tasks |
| `/help` | Show help |

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # Linux / macOS
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and paste your token.
4. Run:
   ```bash
   python bot.py
   ```

## Tech

Python 3.9+, python-telegram-bot 21, SQLite, python-dotenv.
