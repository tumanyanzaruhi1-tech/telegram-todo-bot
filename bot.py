"""Telegram Notes & To-Do bot (python-telegram-bot v21+, SQLite storage)."""
import logging
import os
import sqlite3

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "notes.db")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("notes-bot")

HELP = (
    "Commands:\n"
    "/add <text> - add a task\n"
    "/list - show your tasks\n"
    "/done <id> - mark a task as done\n"
    "/delete <id> - delete a task\n"
    "/clear - delete all your tasks\n"
    "/help - show this message"
)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tasks ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "user_id INTEGER NOT NULL,"
        "text TEXT NOT NULL,"
        "done INTEGER NOT NULL DEFAULT 0)"
    )
    return conn


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "there"
    await update.message.reply_text(f"Hi, {name}! I keep your to-do list.\n\n{HELP}")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /add buy milk")
        return
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (user_id, text) VALUES (?, ?)",
            (update.effective_user.id, text),
        )
    await update.message.reply_text(f"Added #{cur.lastrowid}: {text}")


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with db() as conn:
        rows = conn.execute(
            "SELECT id, text, done FROM tasks WHERE user_id = ? ORDER BY id",
            (update.effective_user.id,),
        ).fetchall()
    if not rows:
        await update.message.reply_text("No tasks yet. Add one with /add")
        return
    lines = [f"{'✅' if d else '⬜'} #{i} {t}" for i, t, d in rows]
    await update.message.reply_text("\n".join(lines))


def _parse_id(context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0].isdigit():
        return int(context.args[0])
    return None


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_id = _parse_id(context)
    if task_id is None:
        await update.message.reply_text("Usage: /done 3")
        return
    with db() as conn:
        cur = conn.execute(
            "UPDATE tasks SET done = 1 WHERE id = ? AND user_id = ?",
            (task_id, update.effective_user.id),
        )
    msg = f"Task #{task_id} done 🎉" if cur.rowcount else "Task not found."
    await update.message.reply_text(msg)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_id = _parse_id(context)
    if task_id is None:
        await update.message.reply_text("Usage: /delete 3")
        return
    with db() as conn:
        cur = conn.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, update.effective_user.id),
        )
    msg = f"Task #{task_id} deleted." if cur.rowcount else "Task not found."
    await update.message.reply_text(msg)


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with db() as conn:
        cur = conn.execute(
            "DELETE FROM tasks WHERE user_id = ?", (update.effective_user.id,)
        )
    await update.message.reply_text(f"Deleted {cur.rowcount} task(s).")


def main():
    if not TOKEN:
        raise SystemExit("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("clear", clear))
    log.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
