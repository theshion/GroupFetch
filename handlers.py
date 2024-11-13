from telethon import TelegramClient
from telethon.sessions import StringSession as TelethonStringSession
from telethon.tl.functions.messages import ExportChatInviteRequest
from pyrogram import Client
from pyrogram.types import StringSession
from pyrogram.types import Message
from pyrogram.session import StringSession as PyrogramStringSession
from kvsqlite.sync import Client as DataClient
from base64 import b64decode
import asyncio
import telebot
from telebot import types
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, UserDeactivatedBanError
from datetime import datetime
from config import API_ID, API_HASH, BOT_TOKEN  # Import from config

data = DataClient("session_data.bot")
bot = telebot.TeleBot(BOT_TOKEN)

sessions = {}
check_with_sessions = {}

def create_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_check = types.KeyboardButton("Start Check")
    add_telethon_session = types.KeyboardButton("Add Telethon Session")
    add_pyrogram_session = types.KeyboardButton("Add Pyrogram Session")
    show_sessions = types.KeyboardButton("Show Sessions")
    show_time = types.KeyboardButton("Current Time")
    programmer = types.KeyboardButton("Programmer")
    programmer_channel = types.KeyboardButton("Programmer's Channel")
    bot_info = types.KeyboardButton("Bot Info")
    markup.add(start_check)
    markup.add(add_telethon_session, add_pyrogram_session, show_sessions, show_time)
    markup.add(bot_info)
    markup.add(programmer, programmer_channel)
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_video(
        message.chat.id,
        "https://t.me/yyyyyy3w/31",
        caption="""
Welcome to the bot for retrieving *your deleted groups*. Send commands now.
Bot programmer: [Shion](t.me/DeityEmperor)
        """,
        parse_mode="Markdown",
        reply_markup=create_buttons()
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    user_id = message.from_user.id

    if text == "Start Check":
        asyncio.run(check_groups(message))
    elif text == "Programmer":
        bot.reply_to(message, "- Bot Programmer: [Shion](t.me/DeityEmperor)", parse_mode="Markdown", disable_web_page_preview=True)
    elif text == "Programmer's Channel":
        bot.reply_to(message, "- Programmer's Channel: [Python Tools](t.me/Coding)", parse_mode="Markdown", disable_web_page_preview=True)
    elif text == "Bot Info":
        bot.reply_to(message, "The bot is simple, no extra info needed. Enjoy!")
    elif text == "Add Telethon Session":
        bot.reply_to(message, "Send the *Telethon* session now", parse_mode="Markdown")
        sessions[user_id] = "add_telethon"
    elif text == "Add Pyrogram Session":
        bot.reply_to(message, "Send the *Pyrogram* session now", parse_mode="Markdown")
        sessions[user_id] = "add_pyrogram"
    elif text == "Show Sessions":
        saved_session = data.get(f"session_{user_id}")
        if saved_session:
            bot.reply_to(message, saved_session)
        else:
            bot.reply_to(message, "No session added!")
    elif user_id in sessions:
        session_data = message.text
        if sessions[user_id] == "add_telethon":
            asyncio.run(handle_telethon_session(message, user_id, session_data))
        elif sessions[user_id] == "add_pyrogram":
            asyncio.run(handle_pyrogram_session(message, user_id, session_data))
        del sessions[user_id]
    elif text == "Current Time":
        current_time = datetime.now().strftime("%I:%M:%S")
        bot.reply_to(message, f"*- Current time is:* `{current_time}`", parse_mode="Markdown")

async def handle_telethon_session(message, user_id, session_data):
    try:
        client = TelegramClient(TelethonStringSession(session_data), API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            raise Exception("Session expired ❌")
        data.set(f"session_{user_id}", session_data)
        bot.reply_to(message, "Telethon session saved ✅")
        check_with_sessions[user_id] = ("telethon", session_data)
        await client.disconnect()
    except Exception:
        bot.reply_to(message, "Telethon session expired ❌")

async def handle_pyrogram_session(message, user_id, session_data):
    try:
        client = PyrogramClient(PyrogramStringSession(session_data), API_ID, API_HASH)
        await client.start()
        me = await client.get_me()
        data.set(f"pyro_session_{user_id}", session_data)
        bot.reply_to(message, f"Pyrogram session saved ✅\nLogged in as: {me.first_name} (@{me.username})")
        check_with_sessions[user_id] = ("pyrogram", session_data)
        await client.stop()
    except Exception:
        bot.reply_to(message, "Pyrogram session expired ❌")

async def check_groups(message):
    user_id = message.from_user.id
    session_type, session_data = check_with_sessions.get(user_id, (None, None))

    if not session_data:
        bot.reply_to(message, "No session added!")
        return

    if session_type == "telethon":
        client = TelegramClient(TelethonStringSession(session_data), API_ID, API_HASH)
    elif session_type == "pyrogram":
        client = PyrogramClient(PyrogramStringSession(session_data), API_ID, API_HASH)
    else:
        bot.reply_to(message, "Invalid session type!")
        return

    async with client:
        # Implement similar group checking logic here
        pass
