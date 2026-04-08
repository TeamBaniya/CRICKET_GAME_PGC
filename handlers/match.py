# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from datetime import datetime
import random
from config import BOWLING_VIDEO_URL, BOWLING_SPEEDS_BUTTONS

# Store active matches
active_matches = {}

async def startgame_command(client, message: Message):
    """Start game command - Directly create match (no overs selection)"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Default 2 overs
    overs = 2
    
    # Create match session
    match_data = {
        "match_id": f"match_{chat_id}_{int(datetime.now().timestamp())}",
        "chat_id": chat_id,
        "total_overs": overs,
        "total_balls": overs * 6,
        "status": "waiting",
        "host_id": user_id,
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
    
    # Add host as first player
    active_matches[chat_id]["players"].append({
        "user_id": user_id,
        "first_name": message.from_user.first_name,
        "username": message.from_user.username,
        "player_number": 1,
        "is_host": True
    })
    
    # Send bowling screen directly
    await send_bowling_screen(client, chat_id, message.from_user.first_name)


async def send_bowling_screen(client, chat_id, bowler_name):
    """Send bowling screen with video and buttons"""
    from handlers.gameplay import active_games as gameplay_games
    
    # Set current bowler
    if chat_id in active_matches:
        game = active_matches[chat_id]
        game["current_bowler"] = game["players"][0]["user_id"]
        game["bowling_status"] = "waiting_for_speed"
    
    # Bowling speed buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("FAST", callback_data="bowl_speed_fast", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("PHYSICAL", callback_data="bowl_speed_physical", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("63", callback_data="bowl_speed_63", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🏏 Bowling", callback_data="bowling_select", style=ButtonStyle.SUCCESS)
        ]
    ])
    
    # Send bowling video
    if BOWLING_VIDEO_URL:
        await client.send_video(
            chat_id,
            video=BOWLING_VIDEO_URL,
            caption=f"🎯 **Hey {bowler_name}, now you're bowling!**\n\nChoose your bowling speed:",
            reply_markup=buttons
        )
    else:
        await client.send_message(
            chat_id,
            f"🎯 **Hey {bowler_name}, now you're bowling!**\n\nChoose your bowling speed:\n\nFAST | PHYSICAL | 63\n\nClick /bowling to start!",
            reply_markup=buttons
        )


async def overs_selected(callback_query, overs):
    """This function is kept for compatibility but not used"""
    # Directly start game without overs selection
    await send_bowling_screen(callback_query._client, callback_query.message.chat.id, callback_query.from_user.first_name)
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
    
    await callback_query.message.edit_text(
        f"🎉 **Game Ready!** 🎉\n\n"
        f"🏏 **2 overs match**\n\n"
        f"**Players joined:**\n{players_list}\n\n"
        f"Type /bowling to start bowling!"
    )


async def set_bowler(callback_query, user_id):
    """Set current bowler"""
    chat_id = callback_query.message.chat.id
    
    if chat_id not in active_matches:
        return False
    
    match = active_matches[chat_id]
    
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
    
    ball_result = {
        "ball_number": match["current_balls"],
        "over": match["current_over"],
        "ball_in_over": match["current_ball_in_over"],
        "runs": runs if not is_wicket else 0,
        "is_wicket": is_wicket,
        "timestamp": datetime.now()
    }
    match["ball_sequence"].append(ball_result)
    
    if match["current_balls"] >= match["total_balls"] or match["current_wickets"] >= 10:
        match["status"] = "completed"
        await db.update_match(match["match_id"], {"status": "completed", "final_score": f"{match['current_runs']}/{match['current_wickets']}"})
    
    return match


async def reset_match(chat_id):
    """Reset match for new game"""
    if chat_id in active_matches:
        del active_matches[chat_id]
    return True


async def get_active_match(chat_id):
    """Get active match for a chat"""
    if chat_id in active_matches:
        return active_matches[chat_id]
    return None
