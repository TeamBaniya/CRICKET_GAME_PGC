from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from handlers.solo import solo_play_number, solo_wicket
from database import db
import random

# Store bowler and batter numbers
bowler_number_store = {}
batter_number_store = {}


async def handle_dm_message(client, message: Message):
    """Handle messages received in bot's DM"""
    user_id = message.from_user.id
    text = message.text.strip()
    text_upper = text.upper()
    
    # ========== DEEP LINK HANDLER (BOWLING) ==========
    if text.startswith("/start bowling_"):
        chat_id_str = text.split("bowling_")[1]
        chat_id = int(chat_id_str)
        
        # Get game info from active_games
        from handlers.gameplay import active_games
        game = active_games.get(chat_id, {})
        
        # Get current batter name
        current_batter_id = game.get("current_batter")
        current_batter_name = "Unknown"
        for player in game.get("players", []):
            if player.get("user_id") == current_batter_id:
                current_batter_name = player.get("first_name")
                break
        
        # Get over/balls info
        current_balls = game.get("current_balls", 0)
        overs_done = current_balls // 6
        balls_done = current_balls % 6
        
        # Create group link button
        group_link = f"https://t.me/c/{str(chat_id).replace('-100', '')}"
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏀 Group", url=group_link, style=ButtonStyle.PRIMARY)]
        ])
        
        # Try to get image URL
        try:
            from config import BOWLING_DM_IMAGE_URL
        except ImportError:
            BOWLING_DM_IMAGE_URL = ""
        
        # Send DM message with batter info
        if BOWLING_DM_IMAGE_URL:
            await message.reply_photo(
                photo=BOWLING_DM_IMAGE_URL,
                caption=f"🎯 **Current batter: {current_batter_name}**\n\n"
                        f"📊 **OVER BALLS = {overs_done}.{balls_done}**\n\n"
                        f"Send your bowling number (1-6)!\n\n"
                        f"⏰ You have 50 seconds!",
                reply_markup=buttons
            )
        else:
            await message.reply_text(
                f"🎯 **Current batter: {current_batter_name}**\n\n"
                f"📊 **OVER BALLS = {overs_done}.{balls_done}**\n\n"
                f"Send your bowling number (1-6)!\n\n"
                f"⏰ You have 50 seconds!\n\n"
                f"Just type a number between 1-6 and send.",
                reply_markup=buttons
            )
        return
    
    # ========== DEEP LINK HANDLER (BATTING) ==========
    if text.startswith("/start batting_"):
        chat_id_str = text.split("batting_")[1]
        chat_id = int(chat_id_str)
        
        # Get game info from active_games
        from handlers.gameplay import active_games
        game = active_games.get(chat_id, {})
        
        # Get current bowler name
        current_bowler_id = game.get("current_bowler")
        current_bowler_name = "Unknown"
        for player in game.get("players", []):
            if player.get("user_id") == current_bowler_id:
                current_bowler_name = player.get("first_name")
                break
        
        # Get over/balls info
        current_balls = game.get("current_balls", 0)
        overs_done = current_balls // 6
        balls_done = current_balls % 6
        
        # Create group link button
        group_link = f"https://t.me/c/{str(chat_id).replace('-100', '')}"
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏀 Group", url=group_link, style=ButtonStyle.PRIMARY)]
        ])
        
        # Try to get image URL
        try:
            from config import BATTING_DM_IMAGE_URL
        except ImportError:
            BATTING_DM_IMAGE_URL = ""
        
        # Send DM message with bowler info
        if BATTING_DM_IMAGE_URL:
            await message.reply_photo(
                photo=BATTING_DM_IMAGE_URL,
                caption=f"🏏 **Current bowler: {current_bowler_name}**\n\n"
                        f"📊 **OVER BALLS = {overs_done}.{balls_done}**\n\n"
                        f"Send your batting number (1-6)!\n\n"
                        f"⏰ You have 50 seconds!",
                reply_markup=buttons
            )
        else:
            await message.reply_text(
                f"🏏 **Current bowler: {current_bowler_name}**\n\n"
                f"📊 **OVER BALLS = {overs_done}.{balls_done}**\n\n"
                f"Send your batting number (1-6)!\n\n"
                f"⏰ You have 50 seconds!\n\n"
                f"Just type a number between 1-6 and send.",
                reply_markup=buttons
            )
        return
    
    # ========== SOLO MODE HANDLING ==========
    from handlers.solo import solo_games
    if user_id in solo_games:
        game = solo_games[user_id]
        if game.get("status") == "batting":
            
            if text_upper == "W":
                result = await solo_wicket(user_id)
                if result:
                    if result.get("is_match_over"):
                        await message.reply_text(
                            f"🎯 **WICKET!** 🎯\n\n"
                            f"📊 **Final Score:** {result['current_score']}\n"
                            f"🏆 **Match Over!**\n\n"
                            f"Type /solo_start to play again!"
                        )
                    else:
                        await message.reply_text(
                            f"🎯 **WICKET!** 🎯\n\n"
                            f"📊 **Score:** {result['current_score']}\n"
                            f"📈 **Balls Left:** {result['balls_left']}\n\n"
                            f"Continue playing! Send next number (1-6)"
                        )
                return
            
            elif text.isdigit() and 1 <= int(text) <= 6:
                number = int(text)
                result = await solo_play_number(user_id, number)
                if result:
                    if result.get("is_match_over"):
                        await message.reply_text(
                            f"🏏 **{result['runs']} RUNS!**\n\n"
                            f"🎉 **Match Completed!** 🎉\n"
                            f"📊 **Final Score:** {result['current_score']}\n"
                            f"🔴 4s: {result['fours']} | 🟢 6s: {result['sixes']}\n\n"
                            f"Type /solo_start to play again!"
                        )
                    else:
                        await message.reply_text(
                            f"🏏 **{result['runs']} RUNS!**\n\n"
                            f"📊 **Score:** {result['current_score']}\n"
                            f"📈 **Balls Left:** {result['balls_left']}\n"
                            f"🔴 4s: {result['fours']} | 🟢 6s: {result['sixes']}\n\n"
                            f"Send next number (1-6)"
                        )
                return
            else:
                await message.reply_text(
                    "❌ **Invalid input!**\n\n"
                    "Send a number between **1-6** to play,\n"
                    "or send **W** for wicket!"
                )
                return
    
    # ========== TEAM MODE - BOWLING HANDLING (DM from bowling button) ==========
    from handlers.gameplay import active_games
    from config import BATTING_VIDEO_URL
    
    for chat_id, game in active_games.items():
        if game.get("current_bowler") == user_id and game.get("bowling_status") == "waiting_for_number":
            if text_upper == "W":
                game["bowling_status"] = "completed"
                bowler_number_store[chat_id] = 0
                await message.reply_text("✅ You chose WICKET! Waiting for batsman...")
                await send_batting_screen_to_group(client, chat_id, game)
                return
                
            elif text.isdigit() and 1 <= int(text) <= 6:
                number = int(text)
                game["bowling_status"] = "completed"
                bowler_number_store[chat_id] = number
                await message.reply_text(f"✅ You sent {number}! Waiting for batsman...")
                await send_batting_screen_to_group(client, chat_id, game)
                return
            else:
                await message.reply_text(
                    "❌ **Invalid input!**\n\n"
                    "Send a number between **1-6** or **W** for wicket!"
                )
                return
    
    # ========== TEAM MODE - BATTING HANDLING (DM from batting button) ==========
    for chat_id, game in active_games.items():
        if game.get("current_batter") == user_id and game.get("batting_status") == "waiting_for_number":
            if text_upper == "W":
                game["batting_status"] = "completed"
                bowler_number_store[chat_id] = 0
                await message.reply_text("✅ You chose WICKET! Waiting for bowler...")
                await send_bowling_screen_to_group(client, chat_id, game)
                return
                
            elif text.isdigit() and 1 <= int(text) <= 6:
                number = int(text)
                game["batting_status"] = "completed"
                bowler_number_store[chat_id] = number
                await message.reply_text(f"✅ You sent {number}! Waiting for bowler...")
                await send_bowling_screen_to_group(client, chat_id, game)
                return
            else:
                await message.reply_text(
                    "❌ **Invalid input!**\n\n"
                    "Send a number between **1-6** or **W** for wicket!"
                )
                return
    
    # Default response
    await message.reply_text(
        "🎮 **Cricket Game Bot**\n\n"
        "You are not in an active game session.\n\n"
        "Start a game with:\n"
        "• /solo_start - Play solo\n"
        "• /startgame - Create team match\n"
        "• /joingame - Join existing game"
    )


async def send_batting_screen_to_group(client, chat_id, game):
    """Send batting screen to group after bowler sends number"""
    from config import BATTING_VIDEO_URL
    
    current_batter_id = game.get("current_batter")
    current_batter_name = "Unknown"
    for player in game.get("players", []):
        if player.get("user_id") == current_batter_id:
            current_batter_name = player.get("first_name")
            break
    
    ratings_text = "ND BAT 66 | MENTAL 66 | PACE 63 | PHYSICAL 66"
    
    await client.send_message(
        chat_id,
        f"🏏 **Now Batter: {current_batter_name} can send number (1-6)!!**\n\n"
        f"📊 **Ratings:** {ratings_text}\n\n"
        f"Type your number (1-6) in this group!"
    )
    
    if BATTING_VIDEO_URL:
        await client.send_video(chat_id, BATTING_VIDEO_URL)
    
    game["batting_status"] = "waiting_for_number"


async def send_bowling_screen_to_group(client, chat_id, game):
    """Send bowling screen to group after batter sends number"""
    from config import BOWLING_VIDEO_URL, BOT_USERNAME
    
    current_bowler_id = game.get("current_bowler")
    current_bowler_name = "Unknown"
    for player in game.get("players", []):
        if player.get("user_id") == current_bowler_id:
            current_bowler_name = player.get("first_name")
            break
    
    await client.send_message(
        chat_id,
        f"🎯 **Now Bowler: {current_bowler_name} can send number (1-6)!!**\n\n"
        f"Click the button below to send your number!"
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏏 Bowling",
                url=f"https://t.me/{BOT_USERNAME}?start=bowling_{chat_id}",
                style=ButtonStyle.PRIMARY
            )
        ]
    ])
    
    if BOWLING_VIDEO_URL:
        await client.send_video(chat_id, BOWLING_VIDEO_URL, reply_markup=buttons)
    else:
        await client.send_message(chat_id, "Click below to bowl!", reply_markup=buttons)
    
    game["bowling_status"] = "waiting_for_number"


async def end_match_team(client, chat_id, game):
    """End team match"""
    current_runs = game.get("current_runs", 0)
    current_wickets = game.get("current_wickets", 0)
    current_balls = game.get("current_balls", 0)
    final_score = f"{current_runs}/{current_wickets}"
    
    await client.send_message(
        chat_id,
        f"🏆 **Match Ended!** 🏆\n\n"
        f"📊 **Final Score:** {final_score}\n"
        f"📈 **Balls Faced:** {current_balls}\n\n"
        f"Thanks for playing! 🎉\n\n"
        f"Type /startgame to play again"
    )
    
    from database import db
    await db.create_match({
        "chat_id": chat_id,
        "score": final_score,
        "balls": current_balls,
        "players": game.get("players", []),
        "created_at": datetime.now()
    })
    
    from handlers.gameplay import active_games
    if chat_id in active_games:
        del active_games[chat_id]
    
    if chat_id in bowler_number_store:
        del bowler_number_store[chat_id]


async def switch_to_next_batsman_team(client, chat_id, game):
    """Switch to next batsman after wicket"""
    players = game.get("players", [])
    current_batter_index = game.get("current_batter_index", 0)
    next_index = current_batter_index + 1
    
    if next_index < len(players):
        next_batter = players[next_index]
        game["current_batter"] = next_batter["user_id"]
        game["current_batter_index"] = next_index
        game["batting_status"] = "waiting_for_number"
        game["bowling_status"] = "waiting_for_number"
        
        await client.send_message(
            chat_id,
            f"🔄 **New batsman! Hey {next_batter['first_name']}, send your number (1-6) in group!**"
        )
    else:
        await end_match_team(client, chat_id, game)


from datetime import datetime
