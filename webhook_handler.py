# webhook_handler.py (for Vercel serverless deployment)
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from main import (
    start, attack_command, stop_command, status_command, 
    services_command, help_command, button_callback, error_handler
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Application.builder().token(BOT_TOKEN).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("attack", attack_command))
app.add_handler(CommandHandler("stop", stop_command))
app.add_handler(CommandHandler("status", status_command))
app.add_handler(CommandHandler("services", services_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_error_handler(error_handler)

async def handle(request):
    """Handle incoming webhook requests"""
    if request.method == "POST":
        body = await request.json()
        update = Update.de_json(body, app.bot)
        await app.process_update(update)
        return {"status": "ok"}
    return {"status": "ok"}

# Vercel handler
def handler(request, context):
    return asyncio.run(handle(request))