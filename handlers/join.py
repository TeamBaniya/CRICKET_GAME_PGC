# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from datetime import datetime, timedelta
import asyncio

# Store active games (import from game.py to use same dictionary)
from handlers.game import active_games

# Try to import image URL, if not exists use empty string
try:
    from config import MEMBERS_LIST_IMAGE_URL, BOWLING_VIDEO_URL
except ImportError:
    MEMBERS_LIST_IMAGE_URL = ""
    BOWLING_VIDEO_URL = ""

join_timers = {}

async def joingame_command(client, message: Message):
    """/joingame command - Join an existing game"""
    user = message.from_user
    chat_id = message.chat.id
    user_id = user.id
    
    # Check if active game exists in this chat
    if chat_id not in active_games:
        await message.reply_text(
            f"😎 {user.first_name}, no game found! Start a new game with /create_game"
        )
        return
    
    game = active_games[chat_id]
    
    # Check if game is still accepting players
    if game["status"] != "waiting":
        await message.reply_text(
            f"🟢 {user.first_name}, the game is not in the joining state!"
        )
        return
    
    # Check if user already joined
    if user_id in [p["user_id"] for p in game["players"]]:
        await message.reply_text(f"✅ {user.first_name}, you already joined the game!")
        return
    
    # Add player
    player_number = len(game["players"]) + 1
    game["players"].append({
        "user_id": user_id,
        "username": user.username,
        "first_name": user.first_name,
        "player_number": player_number,
        "runs": 0,
        "balls": 0,
        "wickets": 0
    })
    
    await message.reply_text(
        f"🏏️ {user.first_name}, you've joined the game! (Player {player_number}) 🏏️"
    )
    
    # Update game message
    await update_game_message(client, chat_id, game)


async def update_game_message(client, chat_id, game):
    """Update the game message with player count"""
    players_list = "\n".join([
        f"  {p['player_number']}. {p.get('first_name', p.get('name', 'Unknown'))}"
        for p in game["players"]
    ])
    
    time_left = (game["expires_at"] - datetime.now()).seconds
    minutes = time_left // 60
    seconds = time_left % 60
    
    game_type = "Solo" if game.get("type") == "solo" else "Team"
    
    new_text = (
        f"🎉 **{game_type} Game Created!** 🎉\n\n"
        f"Join the game using `/joingame` ({minutes}:{seconds:02d} minutes left)\n\n"
        f"**Players joined:**\n{players_list}\n\n"
        f"**Total players:** {len(game['players'])}\n\n"
        f"Game will start automatically when timer ends!"
    )
    
    try:
        msg = await client.get_messages(chat_id, game["message_id"])
        if msg.text != new_text:
            await client.edit_message_text(
                chat_id,
                game["message_id"],
                new_text
            )
    except Exception as e:
        print(f"Error updating game message: {e}")


async def start_timers(client, chat_id):
    """Start all timers for a game"""
    # 60 second warning
    await asyncio.sleep(60)
    if chat_id in active_games and active_games[chat_id]["status"] == "waiting":
        await client.send_message(
            chat_id,
            "⏰ **60 seconds left! Join quickly using /joingame**"
        )
    
    # 30 second warning
    await asyncio.sleep(30)
    if chat_id in active_games and active_games[chat_id]["status"] == "waiting":
        await client.send_message(
            chat_id,
            "⚠️ **30 seconds left only, /joingame !!**"
        )
    
    # 10 second warning
    await asyncio.sleep(20)
    if chat_id in active_games and active_games[chat_id]["status"] == "waiting":
        await client.send_message(
            chat_id,
            "⏰ **Last 10 seconds left only, /joingame !!**"
        )
    
    # 10 more seconds = total 120 seconds (2 minutes)
    await asyncio.sleep(10)
    
    # Auto start game after 2 minutes
    await auto_start_game(client, chat_id)


async def auto_start_game(client, chat_id):
    """Auto start game after timer - Direct bowling screen (no extra message)"""
    if chat_id in active_games:
        game = active_games[chat_id]
        if game["status"] == "waiting":
            game["status"] = "live"
            
            # Send members list image WITHOUT any button
            players_list = ""
            for i, player in enumerate(game["players"], 1):
                username = f"@{player['username']}" if player.get('username') else player['first_name']
                players_list += f"{i}. {username}\n"
            
            caption = f"""🏏 **CRICKET GAME PLAYERS**
🌳 **SOLO TREE COMMUNITY**

**Unknown Host**
**Solo Players**

{players_list}"""
            
            if MEMBERS_LIST_IMAGE_URL:
                await client.send_photo(
                    chat_id,
                    photo=MEMBERS_LIST_IMAGE_URL,
                    caption=caption
                )
            else:
                await client.send_message(chat_id, caption)
            
            # ✅ Set current bowler and batter in active_games (not just match)
            players = game["players"]
            if len(players) >= 2:
                game["current_bowler_index"] = 0
                game["current_batter_index"] = 1
                game["current_bowler"] = players[0]["user_id"]
                game["current_batter"] = players[1]["user_id"]
                game["bowler_name"] = players[0]["first_name"]
                game["bowling_status"] = "waiting_for_number"
                game["batting_status"] = "waiting"
                print(f"🔵 DEBUG: current_bowler set to {game['current_bowler']} (should be {players[0]['user_id']})")
            else:
                game["current_bowler_index"] = 0
                game["current_batter_index"] = 0
                game["current_bowler"] = players[0]["user_id"]
                game["current_batter"] = players[0]["user_id"]
                game["bowler_name"] = players[0]["first_name"]
                game["bowling_status"] = "waiting_for_number"
                print(f"🔵 DEBUG: Solo mode - current_bowler set to {game['current_bowler']}")
            
            # Also set in active_matches for compatibility
            from handlers.match import active_matches
            if chat_id in active_matches:
                active_matches[chat_id]["players"] = game["players"]
                active_matches[chat_id]["current_bowler"] = game["current_bowler"]
                active_matches[chat_id]["current_batter"] = game["current_batter"]
                active_matches[chat_id]["bowling_status"] = "waiting_for_number"
            
            # Directly send bowling screen
            await send_bowling_screen_direct(client, chat_id, game["bowler_name"])


async def send_bowling_screen_direct(client, chat_id, bowler_name):
    """Send bowling screen directly - message then video then button"""
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 Bowling", callback_data="bowling_btn", style=ButtonStyle.PRIMARY)]
    ])
    
    # Send message first
    await client.send_message(
        chat_id,
        f"🎯 **Hey {bowler_name}, now you're bowling!**"
    )
    
    # Wait 2 seconds
    await asyncio.sleep(2)
    
    # Send bowling video with button and caption
    if BOWLING_VIDEO_URL:
        await client.send_video(
            chat_id,
            video=BOWLING_VIDEO_URL,
            caption=f"👏 **{bowler_name} now you can send number on bot pm, You have 1 min.**",
            reply_markup=buttons
        )
    else:
        await client.send_message(
            chat_id,
            f"👏 **{bowler_name} now you can send number on bot pm, You have 1 min.**",
            reply_markup=buttons
        )


async def get_active_game(chat_id):
    """Get active game for a chat"""
    if chat_id in active_games:
        return active_games[chat_id]
    return None


async def delete_active_game(chat_id):
    """Delete active game"""
    if chat_id in active_games:
        del active_games[chat_id]
        return True
    return False


async def add_player_to_game(client, chat_id, user_id, name):
    """Add player to existing game"""
    if chat_id not in active_games:
        return False
    
    game = active_games[chat_id]
    if game["status"] != "waiting":
        return False
    
    if user_id in [p["user_id"] for p in game["players"]]:
        return False
    
    player_number = len(game["players"]) + 1
    game["players"].append({
        "user_id": user_id,
        "username": None,
        "first_name": name,
        "player_number": player_number,
        "runs": 0,
        "balls": 0,
        "wickets": 0
    })
    
    await update_game_message(client, chat_id, game)
    return True
