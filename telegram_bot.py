"""_summary_
    Done! Congratulations on your new bot. You will find it at t.me/flovitrade_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

    Use this token to access the HTTP API:
    7374679860:AAGNP5_IhbEczmQmhqqaxHFoFVeaS-kmNts
    Keep your token secure and store it safely, it can be used by anyone to control your bot.

    For a description of the Bot API, see this page: https://core.telegram.org/bots/api
"""

from typing import Final
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Updater
from screener import parse_tickers
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

TOKEN: Final = '7374679860:AAGNP5_IhbEczmQmhqqaxHFoFVeaS-kmNts'
BOT_USER = 'flovitrade_bot'
CHAT_ID = '-4202997181' # FLOVI Trade

# Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Thanks for chatting with me. I can provide trading tips")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Include me in a group")


async def start_screener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asyncio.create_task(asyncio.to_thread(parse_tickers))
    await update.message.reply_text("Screener started")


# Responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

    print(f"Proccessed text: {processed}")

    if 'hello' in processed:
        return "Hey"
    
    
    return 'say hi gayule'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User({update.message.chat.id}) in group {update.effective_chat.id}, {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USER in text:
            new_text: str = text.replace(BOT_USER, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    print(f'Bot: {response}')
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

async def send_message(bot: Bot, message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

def main() -> None:
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    #app.add_handler(CommandHandler('start', start_command))
    #app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('start_screener', start_screener))
    #app.add_handler(CommandHandler('send', send_message_to_group))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    #await send_message(app.bot, message="Dl. Ovidiu se pune la somn. Drum bun si noapte buna!")
    
    #print('POLLING...')
    app.run_polling(poll_interval=3)


if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            print("Event loop already running. Exiting.")
        else:
            main()
    except RuntimeError:
        main()