# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from datetime import datetime
import random

OVERS_MESSAGE = """
🏏 **Cricket Game**

How many overs do you want for this game?
"""

# Store active matches
active_matches = {}

async def startgame_command(client, message: Message):
    """Start game command - Show overs selection"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if user is host or has permission
    # Overs selection buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1 over", callback_data="overs_1", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("2 overs", callback_data="overs_2", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("3 overs", callback_data="overs_3", style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("4 overs", callback_data="overs_4", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("5 overs", callback_data="overs_5", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("6 overs", callback_data="overs_6", style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("7 overs", callback_data="overs_7", style=ButtonStyle.DEFAULT)
        ]
    ])
    await message.reply_text(OVERS_MESSAGE, reply_markup=buttons)


async def overs_selected(callback_query, overs):
    """Handle overs selection and create match"""
    chat_id = callback_query.message.chat.id
    user = callback_query.from_user
    
    # Create match session
    match_data = {
        "match_id": f"match_{chat_id}_{int(datetime.now().timestamp())}",
        "chat_id": chat_id,
        "total_overs": overs,
        "total_balls": overs * 6,
        "status": "waiting",
        "host_id": user.id,
        "created_at": datetime.now(),
        "current_runs": 0,
        "current_wickets": 0,
        "current_balls": 0,
        "current_over": 0,
        "current_ball_in_over": 0,
        "ball_sequence": [],
        "players": [],
        "current_bowler": None,
        "current_batter": None,
        "current_non_striker": None,
        "bowling_status": "waiting",
        "batting_status": "waiting"
    }
    
    await db.save_session(match_data)
    
    # Store in active matches dict
    active_matches[chat_id] = match_data
    
    # Also add host as first player
    active_matches[chat_id]["players"].append({
        "user_id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "player_number": 1,
        "is_host": True
    })
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 /bowling", callback_data="bowling_select", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("➕ Join Game", callback_data="join_game", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("◀️ BACK", callback_data="back_to_game", style=ButtonStyle.DEFAULT)]
    ])
    
    await callback_query.message.edit_text(
        f"🎉 **OHOO! 👏 Let's play a {overs} overs Match!!**\n\n"
        f"🏏 **Team B will bowl first!**\n\n"
        f"📊 **Match ID:** `{match_data['match_id']}`\n"
        f"👤 **Host:** {user.first_name}\n\n"
        f"Now, type /bowling to choose the bowling member!\n\n"
        f"Or click **Join Game** to participate!",
        reply_markup=buttons
    )
    await callback_query.answer()


async def join_game_callback(callback_query):
    """Handle join game button click"""
    chat_id = callback_query.message.chat.id
    user = callback_query.from_user
    
    if chat_id not in active_matches:
        await callback_query.answer("No active match found! Start a new game with /startgame", show_alert=True)
        return
    
    match = active_matches[chat_id]
    
    # Check if user already joined
    for player in match["players"]:
        if player["user_id"] == user.id:
            await callback_query.answer("You already joined the game!", show_alert=True)
            return
    
    # Add player
    player_number = len(match["players"]) + 1
    match["players"].append({
        "user_id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "player_number": player_number,
        "is_host": False,
        "runs": 0,
        "balls": 0,
        "wickets": 0
    })
    
    await callback_query.answer(f"{user.first_name} joined the game! (Player {player_number})", show_alert=True)
    
    # Update match message
    players_list = "\n".join([f"• Player {p['player_number']}: {p['first_name']}" for p in match["players"]])
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 /bowling", callback_data="bowling_select", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("➕ Join Game", callback_data="join_game", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("◀️ BACK", callback_data="back_to_game", style=ButtonStyle.DEFAULT)]
    ])
    
    await callback_query.message.edit_text(
        f"🎉 **OHOO! 👏 Let's play a {match['total_overs']} overs Match!!**\n\n"
        f"🏏 **Team B will bowl first!**\n\n"
        f"**Players joined:**\n{players_list}\n\n"
        f"Type /bowling to choose the bowling member!",
        reply_markup=buttons
    )


async def set_bowler(callback_query, user_id):
    """Set current bowler"""
    chat_id = callback_query.message.chat.id
    
    if chat_id not in active_matches:
        return False
    
    match = active_matches[chat_id]
    
    # Find player
    for player in match["players"]:
        if player["user_id"] == user_id:
            match["current_bowler"] = user_id
            match["bowling_status"] = "waiting_for_speed"
            return True
    
    return False


async def get_match_status(chat_id):
    """Get current match status"""
    if chat_id in active_matches:
        return active_matches[chat_id]
    return None


async def update_match_score(chat_id, runs, is_wicket=False):
    """Update match score after each ball"""
    if chat_id not in active_matches:
        return None
    
    match = active_matches[chat_id]
    
    if is_wicket:
        match["current_wickets"] += 1
    else:
        match["current_runs"] += runs
    
    match["current_balls"] += 1
    match["current_over"] = match["current_balls"] // 6
    match["current_ball_in_over"] = match["current_balls"] % 6
    
    # Add to ball sequence
    ball_result = {
        "ball_number": match["current_balls"],
        "over": match["current_over"],
        "ball_in_over": match["current_ball_in_over"],
        "runs": runs if not is_wicket else 0,
        "is_wicket": is_wicket,
        "timestamp": datetime.now()
    }
    match["ball_sequence"].append(ball_result)
    
    # Check if innings is over
    if match["current_balls"] >= match["total_balls"] or match["current_wickets"] >= 10:
        match["status"] = "completed"
        await db.update_match(match["match_id"], {"status": "completed", "final_score": f"{match['current_runs']}/{match['current_wickets}]"})
    
    return match


async def reset_match(chat_id):
    """Reset match for new game"""
    if chat_id in active_matches:
        del active_matches[chat_id]
    return True
