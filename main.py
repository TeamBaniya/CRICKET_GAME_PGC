from pyrogram import Client
from pyrogram.types import BotCommand, CallbackQuery
from config import BOT_TOKEN
from handlers import register_handlers

# ✅ Apna API_ID aur API_HASH yahan daalo
API_ID = 30041407
API_HASH = "99e124de540308ca93dc982d167ad67f"

bot = Client(
    "cricket_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

async def setup_commands():
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help"),
        BotCommand("startgame", "Start team match"),
        BotCommand("solo", "Solo mode menu"),
        BotCommand("solo_start", "Start solo match"),
        BotCommand("bowling", "Select bowling speed"),
        BotCommand("batting", "Play as batsman"),
        BotCommand("joingame", "Join existing game"),
        BotCommand("vote_game", "Start voting session"),
        BotCommand("add_A", "Add member to Team A"),
        BotCommand("add_B", "Add member to Team B"),
        BotCommand("join_teamA", "Join Team A"),
        BotCommand("join_teamB", "Join Team B"),
        BotCommand("members_list", "Show team members"),
        BotCommand("end_match", "End current match"),
        BotCommand("feedback", "Give feedback"),
    ]
    await bot.set_bot_commands(commands)

@bot.on_message()
async def main_handler(client, message):
    await register_handlers(client, message)

# ✅ Callback query handler for button clicks
@bot.on_callback_query()
async def callback_handler_wrapper(client, callback_query: CallbackQuery):
    from handlers.callback import callback_handler
    await callback_handler(client, callback_query)

if __name__ == "__main__":
    print("🤖 Cricket Bot Starting...")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    print("📊 Commands registered:")
    print("   • /start - Welcome message")
    print("   • /solo - Solo mode")
    print("   • /startgame - Team match")
    print("   • /bowling /batting - Gameplay")
    print("   • /help - Help menu")
    bot.run()
