from telethon import TelegramClient
from telethon import TelegramClient
from telethon.sessions import StringSession as TelethonStringSession
from telethon.tl.functions.messages import ExportChatInviteRequest
from pyrogram import Client as PyrogramClient, StringSession as PyrogramStringSession
from pyrogram.types import Message
from kvsqlite.sync import Client as DataClient
from base64 import b64decode
import asyncio
import telebot
from telebot import types
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, UserDeactivatedBanError
from datetime import datetime
from config import API_ID, API_HASH, BOT_TOKEN  # Import from config

# Initialize Bot and Data Storage
bot = TeleBot(BOT_TOKEN)
data = DataClient("session_data.bot")

sessions = {}
check_with_sessions = {}

def create_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        "Start Check", "Add Telethon Session", "Add Pyrogram Session",
        "Show Sessions", "Current Time", "Bot Info", "Programmer", "Programmer's Channel"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Welcome to the bot for retrieving your deleted groups.\n"
        "Bot programmer: [Shion](t.me/DeityEmperor)",
        parse_mode="Markdown",
        reply_markup=create_buttons()
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text

    if text == "Start Check":
        asyncio.run(check_groups(message))
    elif text == "Add Telethon Session":
        bot.reply_to(message, "Send the *Telethon* session string now.", parse_mode="Markdown")
        sessions[user_id] = "add_telethon"
    elif text == "Add Pyrogram Session":
        bot.reply_to(message, "Send the *Pyrogram* session string now.", parse_mode="Markdown")
        sessions[user_id] = "add_pyrogram"
    elif text == "Show Sessions":
        saved_session = data.get(f"session_{user_id}")
        bot.reply_to(message, saved_session if saved_session else "No session added!")
    elif user_id in sessions:
        session_data = message.text
        if sessions[user_id] == "add_telethon":
            asyncio.run(handle_telethon_session(message, user_id, session_data))
        elif sessions[user_id] == "add_pyrogram":
            asyncio.run(handle_pyrogram_session(message, user_id, session_data))
        del sessions[user_id]
    elif text == "Current Time":
        bot.reply_to(message, f"Current time is: `{datetime.now().strftime('%I:%M:%S')}`", parse_mode="Markdown")
    elif text == "Programmer":
        bot.reply_to(message, "Bot Programmer: [Shion](t.me/DeityEmperor)", parse_mode="Markdown")
    elif text == "Programmer's Channel":
        bot.reply_to(message, "Programmer's Channel: [Python Tools](t.me/Coding)", parse_mode="Markdown")
    elif text == "Bot Info":
        bot.reply_to(message, "This bot helps you manage and retrieve deleted groups.")

async def handle_telethon_session(message, user_id, session_data):
    try:
        client = TelegramClient(TelethonStringSession(session_data), API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            raise Exception("Session expired.")
        data.set(f"session_{user_id}", session_data)
        bot.reply_to(message, "Telethon session saved ✅")
        check_with_sessions[user_id] = ("telethon", session_data)
        await client.disconnect()
    except SessionPasswordNeededError:
        bot.reply_to(message, "Telethon session requires 2SV password.")
    except Exception as e:
        bot.reply_to(message, f"Telethon session expired or invalid: {e}")

async def handle_pyrogram_session(message, user_id, session_data):
    try:
        client = PyrogramClient(PyrogramStringSession(session_data), API_ID, API_HASH)
        await client.start()
        me = await client.get_me()
        data.set(f"pyro_session_{user_id}", session_data)
        bot.reply_to(message, f"Pyrogram session saved ✅\nLogged in as: {me.first_name} (@{me.username})")
        check_with_sessions[user_id] = ("pyrogram", session_data)
        await client.stop()
    except SessionPasswordNeeded:
        bot.reply_to(message, "Pyrogram session requires 2SV password.")
    except AuthKeyUnregistered:
        bot.reply_to(message, "Pyrogram session is unregistered or expired.")
    except Exception as e:
        bot.reply_to(message, f"Pyrogram session expired or invalid: {e}")

async def check_groups(message):
    user_id = message.from_user.id
    session_type, session_data = check_with_sessions.get(user_id, (None, None))

    if not session_data:
        bot.reply_to(message, "No session added!")
        return

    client = None
    if session_type == "telethon":
        client = TelegramClient(TelethonStringSession(session_data), API_ID, API_HASH)
    elif session_type == "pyrogram":
        client = PyrogramClient(PyrogramStringSession(session_data), API_ID, API_HASH)

    if client:
        async with client:
            # Add group-checking logic here.
            await bot.reply_to(message, f"Session ({session_type}) is valid!")
    else:
        bot.reply_to(message, "Invalid session type!")

bot.polling()
