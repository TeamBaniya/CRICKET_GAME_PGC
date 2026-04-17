from pyrogram import Client
from handlers import register_handlers, callback_handler
import asyncio
import os

API_ID = YOUR_API_ID
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

app = Client(
    "cricket_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message()
async def message_handler(client, message):
    await register_handlers(client, message)

@app.on_callback_query()
async def callback_query_handler(client, callback_query):
    await callback_handler(client, callback_query)

async def main():
    print("🤖 Cricket Game Bot is starting...")
    await app.start()
    print("✅ Bot is now running!")
    print("Press Ctrl+C to stop the bot")
    await asyncio.Event().wait()  # Keep the bot running

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
