from pyrogram import Client
from pyrogram.types import BotCommand
from config import BOT_TOKEN
from handlers import register_handlers

# ✅ Apna API_ID aur API_HASH yahan daalo
API_ID = 20138139 # <-- Apna ID daalo (number hai)
API_HASH = "ff813495ed17a07723000a9751f4c3ee"  # <-- Apna Hash daalo (string hai)

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
        BotCommand("feedback", "Give feedback"),
    ]
    await bot.set_bot_commands(commands)

@bot.on_message()
async def main_handler(client, message):
    await register_handlers(client, message)

if __name__ == "__main__":
    print("🤖 Bot Starting...")
    bot.run()
