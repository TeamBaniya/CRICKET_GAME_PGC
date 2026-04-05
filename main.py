from pyrogram import Client
from pyrogram.types import BotCommand, CallbackQuery
from config import BOT_TOKEN
from handlers import register_handlers

# ✅ Apna API_ID aur API_HASH yahan daalo
API_ID = 20138139
API_HASH = "ff813495ed17a07723000a9751f4c3ee"

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
        BotCommand("startgame", "Start the game"),
        BotCommand("bowling", "Choose bowler"),
        BotCommand("batting", "Choose batsman"),
        BotCommand("add_A", "Add member to Team A"),
        BotCommand("add_B", "Add member to Team B"),
        BotCommand("join_teamA", "Join Team A"),
        BotCommand("join_teamB", "Join Team B"),
        BotCommand("end_match", "End current match"),
        BotCommand("solo", "Solo mode"),
        BotCommand("solo_start", "Start solo match"),
        BotCommand("joingame", "Join game"),
        BotCommand("vote_game", "Start voting session"),
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
    print("🤖 Bot Starting...")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    bot.run()
