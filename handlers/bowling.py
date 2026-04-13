from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
import asyncio
from handlers.game import active_games
from config import BOWLING_VIDEO_URL, BOT_USERNAME

bowler_number_store = {}

async def bowling_command(client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if chat_id not in active_games:
        await message.reply_text("❌ No active game found!")
        return
    
    game = active_games[chat_id]
    if game.get("current_bowler") != user_id:
        await message.reply_text("❌ You are not the bowler!")
        return
    
    game["bowling_status"] = "waiting_for_number"
    game["bowler_name"] = message.from_user.first_name
    game["bowler_id"] = user_id
    
    # Send message first
    await message.reply_text(
        f"🎯 **Hey {message.from_user.first_name}, now you're bowling!**\n\n"
        f"⏰ You have 60 seconds!\n\n"
        f"Click the button below to send your number!"
    )
    
    await asyncio.sleep(2)
    
    # Deep link button
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 Bowling", url=f"https://t.me/{BOT_USERNAME}?start=bowling_{chat_id}", style=ButtonStyle.PRIMARY)]
    ])
    
    if BOWLING_VIDEO_URL:
        await client.send_video(chat_id, BOWLING_VIDEO_URL, caption=f"👏 **{message.from_user.first_name} click below to send your number!**", reply_markup=buttons)
    else:
        await client.send_message(chat_id, f"👏 **{message.from_user.first_name} click below to send your number!**", reply_markup=buttons)
    
    # Start 50 second timer
    await start_bowling_timer(client, chat_id, message.from_user.first_name, user_id)

async def start_bowling_timer(client, chat_id, bowler_name, bowler_id):
    for remaining in range(50, 0, -1):
        if chat_id not in active_games:
            return
        game = active_games[chat_id]
        if game.get("bowling_status") != "waiting_for_number":
            return
        await asyncio.sleep(1)
    
    if chat_id in active_games and active_games[chat_id].get("bowling_status") == "waiting_for_number":
        game = active_games[chat_id]
        await client.send_message(chat_id, f"⏰ **@{bowler_name} didn't send number in 50 seconds! Eliminated from the game!**")
        
        players = game.get("players", [])
        for i, player in enumerate(players):
            if player.get("user_id") == bowler_id:
                players.pop(i)
                break
        game["players"] = players
        
        if len(players) == 0:
            from handlers.result import end_match
            await end_match(client, None, chat_id)
            return
        
        if len(players) > 0:
            game["current_batter"] = players[0]["user_id"]
            game["batting_status"] = "waiting_for_number"
            from handlers.batting import send_batting_screen
            await send_batting_screen(client, chat_id, players[0]["first_name"])

async def bowling_dm_handler(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if not text.isdigit() or not (1 <= int(text) <= 6):
        await message.reply_text("❌ Please send a number between 1-6!")
        return
    
    number = int(text)
    
    for chat_id, game in active_games.items():
        if game.get("current_bowler") == user_id and game.get("bowling_status") == "waiting_for_number":
            game["bowling_status"] = "completed"
            bowler_number_store[chat_id] = number
            await message.reply_text(f"✅ You sent {number}! Waiting for batsman...")
            
            # Send batting screen to group
            from handlers.batting import send_batting_screen
            await send_batting_screen(client, chat_id, game["players"][game.get("current_batter_index", 0)]["first_name"])
            return
