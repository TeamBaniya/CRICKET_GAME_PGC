# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ButtonStyle
from config import BOWLING_SPEEDS_BUTTONS, BOWLING_VIDEO_URL
import random
import asyncio

# Store bowling sessions
bowling_sessions = {}
bowling_timers = {}


async def bowling_command(client, message: Message):
    """/bowling command - Bowl as bowler"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    args = message.text.split()
    
    # Check if user is the current bowler
    from handlers.gameplay import active_games
    if chat_id not in active_games:
        await message.reply_text("❌ No active game found! Use /startgame first.")
        return
    
    game = active_games[chat_id]
    if game.get("current_bowler") != user_id:
        await message.reply_text("❌ You are not the current bowler!")
        return
    
    if len(args) < 2:
        # Show bowling speed options
        buttons = []
        row = []
        for i, speed in enumerate(BOWLING_SPEEDS_BUTTONS):
            row.append(InlineKeyboardButton(speed, callback_data=f"bowl_speed_{speed.lower()}", style=ButtonStyle.PRIMARY))
            if len(row) == 3:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        
        buttons.append([InlineKeyboardButton("◀️ BACK", callback_data="back_to_game", style=ButtonStyle.DEFAULT)])
        
        await message.reply_text(
            f"🎯 **Hey {message.from_user.first_name}, now you're bowling!**\n\n"
            f"📊 **Choose your bowling speed:**\n\n"
            f"• Click on speed button\n"
            f"• Or use /bowling <speed>\n\n"
            f"Example: /bowling FAST",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    speed = args[1].upper()
    if speed not in BOWLING_SPEEDS_BUTTONS:
        await message.reply_text(
            f"❌ Invalid speed! Choose from:\n{', '.join(BOWLING_SPEEDS_BUTTONS)}"
        )
        return
    
    await process_bowling_speed(client, chat_id, user_id, speed, message)


async def process_bowling_speed(client, chat_id, user_id, speed, message=None):
    """Process bowling speed selection and start timer"""
    from handlers.gameplay import active_games, bowler_number_store
    
    if chat_id not in active_games:
        if message:
            await message.reply_text("❌ No active game found!")
        return
    
    game = active_games[chat_id]
    game["selected_speed"] = speed
    game["bowling_status"] = "waiting_for_number"
    
    # Send bowling video
    if BOWLING_VIDEO_URL:
        await client.send_video(chat_id, BOWLING_VIDEO_URL, caption=f"🎯 **Speed {speed} selected!**")
    
    await client.send_message(
        chat_id,
        f"✅ **Speed {speed} selected!**\n\n"
        f"Now send number on bot PM (1-6 or W for wicket)\n"
        f"⏰ You have 60 seconds!"
    )
    
    if message:
        await message.reply_text(f"✅ Speed {speed} selected! Send number on bot PM!")
    
    # Start 60 second timer
    await start_bowling_timer_team(client, chat_id, game.get("current_bowler_name", "Bowler"))


async def start_bowling_timer_team(client, chat_id, bowler_name):
    """60 second timer for bowler to send number in team mode"""
    from handlers.gameplay import active_games
    
    for remaining in range(60, 0, -1):
        if chat_id not in active_games:
            return
        
        game = active_games[chat_id]
        if game.get("bowling_status") != "waiting_for_number":
            return
        
        if remaining == 30:
            await client.send_message(
                chat_id,
                f"⚠️ **Warning: {bowler_name}, you have 30 seconds left to send a number!**"
            )
        elif remaining == 10:
            await client.send_message(
                chat_id,
                f"⚠️ **Warning: {bowler_name}, you have 10 seconds left to send a number!**"
            )
        
        await asyncio.sleep(1)
    
    # Timeout - penalty
    if chat_id in active_games and active_games[chat_id].get("bowling_status") == "waiting_for_number":
        await client.send_message(
            chat_id,
            "⏰ **No message received from bowler, deducting 6 runs of bowler.**\n\n"
            "❌ **Seems Bowling player is not responding, User Eliminated from the game !!**"
        )
        
        # Switch to next bowler
        await switch_to_next_bowler_team(client, chat_id)


async def switch_to_next_bowler_team(client, chat_id):
    """Switch to next bowler after timeout or wicket"""
    from handlers.gameplay import active_games
    
    if chat_id not in active_games:
        return
    
    game = active_games[chat_id]
    players = game.get("players", [])
    if not players:
        return
    
    current_index = game.get("current_bowler_index", 0)
    next_index = (current_index + 1) % len(players)
    next_bowler = players[next_index]
    
    game["current_bowler"] = next_bowler["user_id"]
    game["current_bowler_index"] = next_index
    game["bowling_status"] = "waiting_for_speed"
    game["current_bowler_name"] = next_bowler["first_name"]
    
    await client.send_message(
        chat_id,
        f"🔄 **Hey {next_bowler['first_name']}, now you're bowling!**\n\n"
        f"Use /bowling <speed> to select your speed!"
    )


async def bowling_speed_callback(callback_query: CallbackQuery):
    """Handle bowling speed button clicks"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    if data.startswith("bowl_speed_"):
        speed = data.split("_")[2].upper()
        
        # Create fake message for process_bowling_speed
        class FakeMessage:
            def __init__(self, from_user, reply_text):
                self.from_user = from_user
                self.reply_text = reply_text
        
        fake_msg = FakeMessage(callback_query.from_user, callback_query.message.reply_text)
        await process_bowling_speed(callback_query._client, chat_id, user_id, speed, fake_msg)
        await callback_query.answer()


async def show_bowling_speed_options(callback_query: CallbackQuery):
    """Show bowling speed options in group"""
    from handlers.gameplay import active_games
    chat_id = callback_query.message.chat.id
    
    if chat_id not in active_games:
        await callback_query.answer("No active game!", show_alert=True)
        return
    
    game = active_games[chat_id]
    user_id = callback_query.from_user.id
    
    if game.get("current_bowler") != user_id:
        await callback_query.answer("You are not the current bowler!", show_alert=True)
        return
    
    buttons = []
    row = []
    for i, speed in enumerate(BOWLING_SPEEDS_BUTTONS):
        row.append(InlineKeyboardButton(speed, callback_data=f"bowl_speed_{speed.lower()}", style=ButtonStyle.PRIMARY))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("◀️ BACK", callback_data="back_to_game", style=ButtonStyle.DEFAULT)])
    
    await callback_query.message.edit_text(
        f"🎯 **Choose your bowling speed:**\n\n"
        f"Available speeds: {', '.join(BOWLING_SPEEDS_BUTTONS)}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await callback_query.answer()
