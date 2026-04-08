# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from datetime import datetime, timedelta
import asyncio
from config import MEMBERS_LIST_IMAGE_URL

# Store active games (import from game.py to use same dictionary)
from handlers.game import active_games

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


async def start_join_warnings(client, chat_id):
    """Send 10 seconds warning before game expires"""
    await asyncio.sleep(110)  # 1 minute 50 seconds (2 min - 10 sec)
    
    if chat_id in active_games and active_games[chat_id]["status"] == "waiting":
        await client.send_message(
            chat_id,
            "⏰ **Last 10 seconds left only, /joingame !!**"
        )


async def auto_start_game(client, chat_id):
    """Auto start game after timer and send members list image"""
    # Wait for 2 minutes
    await asyncio.sleep(120)
    
    if chat_id in active_games:
        game = active_games[chat_id]
        if game["status"] == "waiting":
            game["status"] = "starting"
            
            # Send members list image with players
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
            
            # Wait 10 more seconds
            await asyncio.sleep(10)
            
            # Start the game
            game["status"] = "live"
            await client.send_message(
                chat_id,
                f"🏏 **GAME STARTING!** 🏏\n\n"
                f"👥 Total players: {len(game['players'])}\n\n"
                f"👉 **{game['players'][0]['first_name']}**, you're bowling first!\n\n"
                f"Use /bowling to start!"
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
