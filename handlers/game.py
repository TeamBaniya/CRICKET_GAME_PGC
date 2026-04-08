from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram.enums import ButtonStyle
from datetime import datetime, timedelta
import asyncio
from config import SOLO_GAME_START_IMAGE

# Store active games (shared with join.py)
active_games = {}

async def create_game_command(client, message: Message):
    """/create_game command - Show game type selection"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Solo", callback_data="create_solo", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("👥 Team", callback_data="create_team", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("◀️ BACK", callback_data="back_to_main", style=ButtonStyle.DEFAULT)
        ]
    ])
    
    await message.reply_text(
        "🎮 **Create Game**\n\n"
        "Choose game type:",
        reply_markup=buttons
    )


async def create_solo_game(callback_query):
    """Create solo game (2 minutes join time)"""
    chat_id = callback_query.message.chat.id
    user = callback_query.from_user
    
    # Store game in active_games
    active_games[chat_id] = {
        "type": "solo",
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=2),
        "players": [{
            "user_id": user.id, 
            "name": user.first_name, 
            "player_number": 1,
            "username": user.username,
            "runs": 0,
            "balls": 0,
            "wickets": 0
        }],
        "status": "waiting",
        "host_id": user.id,
        "message_id": callback_query.message.id
    }
    
    await callback_query.message.edit_text(
        f"🎉 **Solo Game Created!** 🎉\n\n"
        f"👤 **Host:** {user.first_name}\n"
        f"👥 **Players joined:** 1\n\n"
        f"Join the game using `/joingame` (2 minutes to join)\n\n"
        f"⏰ You have 2 minutes to join!\n\n"
        f"Type `/startgame` when ready!"
    )
    
    # Start auto-start timer for solo game
    asyncio.create_task(auto_start_solo_game(callback_query._client, chat_id))
    
    await callback_query.answer()


async def auto_start_solo_game(client, chat_id):
    """Auto start solo game after 2 minutes"""
    await asyncio.sleep(120)  # 2 minutes
    
    if chat_id in active_games:
        game = active_games[chat_id]
        if game["status"] == "waiting":
            game["status"] = "starting"
            await send_solo_game_start_image(client, chat_id, game)


async def send_solo_game_start_image(client, chat_id, game):
    """Send image with players list before game starts"""
    players_list = ""
    for i, player in enumerate(game["players"], 1):
        username = f"@{player['username']}" if player.get('username') else player['name']
        players_list += f"{i}. {username}\n"
    
    caption = f"""🏏 **CRICKET GAME PLAYERS**
🌳 **SOLO TREE COMMUNITY**

**Unknown Host**
**Solo Players**

{players_list}"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Start Game", callback_data="start_solo_match", style=ButtonStyle.SUCCESS)]
    ])
    
    await client.send_photo(
        chat_id,
        photo=SOLO_GAME_START_IMAGE,
        caption=caption,
        reply_markup=buttons
    )


async def start_solo_match_callback(callback_query):
    """Start solo match after image is shown"""
    chat_id = callback_query.message.chat.id
    
    if chat_id in active_games:
        game = active_games[chat_id]
        game["status"] = "live"
        
        await callback_query.message.edit_text(
            "🏏 **SOLO MATCH STARTING!** 🏏\n\n"
            f"👥 Total players: {len(game['players'])}\n\n"
            "Each player will bat one by one!\n\n"
            f"👉 **{game['players'][0]['name']}**, you're batting first!\n\n"
            "Send numbers 1-6 on bot PM to play!"
        )
    await callback_query.answer()


async def create_team_game(callback_query):
    """Create team game (2 minutes join time)"""
    chat_id = callback_query.message.chat.id
    user = callback_query.from_user
    
    # Store game in active_games
    active_games[chat_id] = {
        "type": "team",
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=2),
        "players": [{
            "user_id": user.id, 
            "name": user.first_name, 
            "player_number": 1, 
            "username": user.username,
            "team": None,
            "runs": 0,
            "balls": 0,
            "wickets": 0
        }],
        "status": "waiting",
        "host_id": user.id,
        "message_id": callback_query.message.id
    }
    
    await callback_query.message.edit_text(
        f"👥 **Team Game Created!** 👥\n\n"
        f"👤 **Host:** {user.first_name}\n"
        f"👥 **Players joined:** 1\n\n"
        f"Join the game using `/joingame` (2 minutes to join)\n\n"
        f"⏰ You have 2 minutes to join!\n\n"
        f"Type `/startgame` when ready!\n\n"
        f"Use `/add_A` and `/add_B` to assign teams!"
    )
    await callback_query.answer()


async def get_active_game(chat_id):
    """Get active game for a chat"""
    return active_games.get(chat_id)


async def delete_active_game(chat_id):
    """Delete active game"""
    if chat_id in active_games:
        del active_games[chat_id]
        return True
    return False


async def update_game_message(client, chat_id, game):
    """Update the game message with player count"""
    players_list = "\n".join([
        f"  {p['player_number']}. {p['name']}"
        for p in game["players"]
    ])
    
    time_left = (game["expires_at"] - datetime.now()).seconds
    minutes = time_left // 60
    seconds = time_left % 60
    
    game_type = "Solo" if game["type"] == "solo" else "Team"
    
    try:
        await client.edit_message_text(
            chat_id,
            game["message_id"],
            f"🎉 **{game_type} Game Created!** 🎉\n\n"
            f"Join the game using `/joingame` ({minutes}:{seconds:02d} minutes left)\n\n"
            f"**Players joined:**\n{players_list}\n\n"
            f"**Total players:** {len(game['players'])}\n\n"
            f"Type `/startgame` when ready!"
        )
    except:
        pass
