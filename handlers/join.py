# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from datetime import datetime, timedelta
import asyncio

# Store active games
active_games = {}
join_timers = {}

async def joingame_command(client, message: Message):
    """/joingame command - Join an existing game"""
    user = message.from_user
    chat_id = message.chat.id
    user_id = user.id
    
    # Check if active game exists in this chat
    if chat_id not in active_games:
        await message.reply_text(
            f"😎 {user.first_name}, no game found! Start a new game with /start"
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
        "player_number": player_number
    })
    
    await message.reply_text(
        f"🏏️ {user.first_name}, you've joined the game! (Player {player_number}) 🏏️"
    )
    
    # Update game message
    await update_game_message(client, chat_id, game)


async def create_game(client, message: Message, host_id: int):
    """Create a new game (called from vote_game or host selection)"""
    chat_id = message.chat.id
    
    game = {
        "host_id": host_id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=2),
        "players": [],
        "status": "waiting",  # waiting, live, completed, expired
        "message_id": None,
        "total_overs": 2,
        "current_runs": 0,
        "current_wickets": 0,
        "current_balls": 0,
        "ball_sequence": []
    }
    
    # Add host as first player
    try:
        host_user = await client.get_users(host_id)
        game["players"].append({
            "user_id": host_id,
            "username": host_user.username,
            "first_name": host_user.first_name,
            "player_number": 1,
            "is_host": True
        })
    except:
        game["players"].append({
            "user_id": host_id,
            "username": None,
            "first_name": "Host",
            "player_number": 1,
            "is_host": True
        })
    
    active_games[chat_id] = game
    
    # Send game creation message
    msg = await message.reply_text(
        f"🎉 **Game created!** Join the game using `/joingame` (2 minutes to join) 🏏️\n\n"
        f"**Host:** {game['players'][0]['first_name']}\n"
        f"**Players joined:** 1"
    )
    game["message_id"] = msg.id
    
    # Start auto-expire timer
    asyncio.create_task(auto_expire_game(client, chat_id))
    
    # Start warning timers
    asyncio.create_task(start_join_warnings(client, chat_id))


async def start_join_warnings(client, chat_id):
    """Send warnings before game expires"""
    await asyncio.sleep(110)  # 1 minute 50 seconds
    
    if chat_id in active_games and active_games[chat_id]["status"] == "waiting":
        await client.send_message(
            chat_id,
            "⏰ **Last 10 seconds left only, /joingame !!**"
        )


async def auto_expire_game(client, chat_id):
    """Auto expire game after 2 minutes if not started"""
    await asyncio.sleep(120)  # 2 minutes
    
    if chat_id in active_games:
        game = active_games[chat_id]
        if game["status"] == "waiting":
            game["status"] = "expired"
            await client.send_message(
                chat_id,
                "⚠️ **Voting session expired due to inactivity.**\n\n"
                f"Players joined: {len(game['players'])}\n\n"
                "Start a new game with /start"
            )
            del active_games[chat_id]


async def update_game_message(client, chat_id, game):
    """Update the game message with player count"""
    players_list = "\n".join([
        f"  {p['player_number']}. {p['first_name']}"
        for p in game["players"]
    ])
    
    time_left = (game["expires_at"] - datetime.now()).seconds
    minutes = time_left // 60
    seconds = time_left % 60
    
    try:
        await client.edit_message_text(
            chat_id,
            game["message_id"],
            f"🎉 **Game created!** Join the game using `/joingame` ({minutes}:{seconds:02d} minutes left) 🏏️\n\n"
            f"**Players joined:**\n{players_list}\n\n"
            f"**Total players:** {len(game['players'])}\n\n"
            f"Type `/startgame` when ready!"
        )
    except:
        pass


async def start_game_from_join(client, chat_id):
    """Start the game when enough players join"""
    if chat_id not in active_games:
        return
    
    game = active_games[chat_id]
    if game["status"] != "waiting":
        return
    
    if len(game["players"]) < 2:
        return
    
    game["status"] = "live"
    
    await client.send_message(
        chat_id,
        f"🏏 **MATCH STARTING!** 🏏\n\n"
        f"Total players: {len(game['players'])}\n\n"
        f"🎲 **Toss time!**\n\n"
        f"Use /bowling <speed> to select bowler\n"
        f"Use /batting <number> to play!"
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
    if chat_id in join_timers:
        join_timers[chat_id].cancel()
