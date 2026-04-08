from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from datetime import datetime, timedelta
import asyncio

# Store active games
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
        "players": [{"user_id": user.id, "name": user.first_name, "player_number": 1}],
        "status": "waiting",
        "host_id": user.id
    }
    
    await callback_query.message.edit_text(
        f"🎉 **Solo Game Created!** 🎉\n\n"
        f"👤 **Host:** {user.first_name}\n"
        f"👥 **Players joined:** 1\n\n"
        f"Join the game using `/joingame` (2 minutes to join)\n\n"
        f"⏰ You have 2 minutes to join!\n\n"
        f"Type `/startgame` when ready!"
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
        "players": [{"user_id": user.id, "name": user.first_name, "player_number": 1, "team": None}],
        "status": "waiting",
        "host_id": user.id
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
