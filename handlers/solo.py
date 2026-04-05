# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ButtonStyle
from database import db
from datetime import datetime
import random
import asyncio

# Store active solo games
solo_games = {}
solo_timers = {}

# Solo player icons
SOLO_ICONS = ["🟢", "⚽", "🔥", "🌞", "💬", "🎮", "🏀", "🐍", "🕊️", "⭐", "⚡", "💎"]

async def solo_play_command(client, message: Message):
    """Solo play command - Show solo mode menu"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎮 Start Solo Match", callback_data="solo_start", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("📊 My Stats", callback_data="solo_stats", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="solo_leaderboard", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)
        ]
    ])
    
    await message.reply_text(
        "🎯 **SOLO MODE**\n\n"
        "Play cricket matches against the bot!\n\n"
        "• **Start Solo Match** - Play a new match\n"
        "• **My Stats** - View your statistics\n"
        "• **Leaderboard** - Top players list\n\n"
        "Send numbers 1-6 to play your shots!",
        reply_markup=buttons
    )


async def solo_start_command(client, message: Message):
    """Start a solo match"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Check if already in game
    if user_id in solo_games:
        await message.reply_text("❌ You already have an active solo game! Finish it first.")
        return
    
    # Create new solo game
    solo_games[user_id] = {
        "user_id": user_id,
        "user_name": user_name,
        "runs": 0,
        "balls": 0,
        "wickets": 0,
        "fours": 0,
        "sixes": 0,
        "ball_sequence": [],
        "status": "batting",
        "current_ball": 0,
        "max_balls": 12,  # 2 overs
        "created_at": datetime.now()
    }
    
    # Get or create solo player stats
    player = await db.get_solo_player(user_id)
    if not player:
        icon = SOLO_ICONS[user_id % len(SOLO_ICONS)]
        await db.save_solo_player({
            "user_id": user_id,
            "name": user_name,
            "icon": icon,
            "total_runs": 0,
            "total_balls": 0,
            "total_fours": 0,
            "total_sixes": 0,
            "total_matches": 0,
            "highest_score": 0,
            "ball_sequences": [],
            "created_at": datetime.now()
        })
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 Play Ball", callback_data="solo_play_ball", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("❌ End Match", callback_data="solo_end_match", style=ButtonStyle.DANGER)]
    ])
    
    await message.reply_text(
        f"🏏 **SOLO MATCH STARTED!**\n\n"
        f"👤 **Player:** {user_name}\n"
        f"📊 **Format:** 2 overs (12 balls)\n\n"
        f"🎯 **Ratings:** ND BAT | MENTAL 66 | PACE 63 | PHYSICAL 66\n\n"
        f"Send numbers **1-6** on bot PM to play your shots!\n"
        f"Type **W** for wicket (if you want to get out!)\n\n"
        f"Click **Play Ball** to start!",
        reply_markup=buttons
    )


async def solo_play_ball_callback(callback_query: CallbackQuery):
    """Handle solo play ball"""
    user_id = callback_query.from_user.id
    
    if user_id not in solo_games:
        await callback_query.answer("No active solo game! Use /solo_start", show_alert=True)
        return
    
    game = solo_games[user_id]
    
    if game["status"] != "batting":
        await callback_query.answer("Game already finished!", show_alert=True)
        return
    
    await callback_query.message.edit_text(
        f"🏏 **PLAY BALL!**\n\n"
        f"📊 **Current Score:** {game['runs']}/{game['wickets']}\n"
        f"📈 **Balls:** {game['current_ball']}/{game['max_balls']}\n"
        f"🎯 **Ratings:** ND BAT | MENTAL 66 | PACE 63 | PHYSICAL 66\n\n"
        f"**Send number (1-6) on bot PM!**"
    )
    await callback_query.answer()


async def solo_play_number(user_id: int, number: int):
    """Process solo play number"""
    if user_id not in solo_games:
        return None
    
    game = solo_games[user_id]
    
    if game["status"] != "batting":
        return None
    
    # Calculate runs based on number
    runs = number  # Simple logic - number = runs
    
    # Update game stats
    game["runs"] += runs
    game["balls"] += 1
    game["current_ball"] += 1
    game["ball_sequence"].append(runs)
    
    if runs == 4:
        game["fours"] += 1
    elif runs == 6:
        game["sixes"] += 1
    
    # Check if match over
    is_match_over = game["current_ball"] >= game["max_balls"] or game["wickets"] >= 10
    
    result = {
        "runs": runs,
        "is_match_over": is_match_over,
        "current_score": f"{game['runs']}/{game['wickets']}",
        "balls_left": game["max_balls"] - game["current_ball"],
        "fours": game["fours"],
        "sixes": game["sixes"],
        "ball_sequence": game["ball_sequence"]
    }
    
    if is_match_over:
        await save_solo_match_result(user_id, game)
        solo_games[user_id]["status"] = "completed"
    
    return result


async def solo_wicket(user_id: int):
    """Process wicket in solo mode"""
    if user_id not in solo_games:
        return None
    
    game = solo_games[user_id]
    
    if game["status"] != "batting":
        return None
    
    game["wickets"] += 1
    game["balls"] += 1
    game["current_ball"] += 1
    game["ball_sequence"].append("W")
    
    is_match_over = game["current_ball"] >= game["max_balls"] or game["wickets"] >= 10
    
    result = {
        "is_wicket": True,
        "is_match_over": is_match_over,
        "current_score": f"{game['runs']}/{game['wickets']}",
        "balls_left": game["max_balls"] - game["current_ball"]
    }
    
    if is_match_over:
        await save_solo_match_result(user_id, game)
        solo_games[user_id]["status"] = "completed"
    
    return result


async def save_solo_match_result(user_id: int, game: dict):
    """Save solo match result to database"""
    # Update player stats
    player = await db.get_solo_player(user_id)
    if player:
        new_total_runs = player.get("total_runs", 0) + game["runs"]
        new_total_balls = player.get("total_balls", 0) + game["balls"]
        new_total_fours = player.get("total_fours", 0) + game["fours"]
        new_total_sixes = player.get("total_sixes", 0) + game["sixes"]
        new_total_matches = player.get("total_matches", 0) + 1
        new_highest = max(player.get("highest_score", 0), game["runs"])
        
        await db.save_solo_player({
            "user_id": user_id,
            "name": game["user_name"],
            "icon": player.get("icon", SOLO_ICONS[user_id % len(SOLO_ICONS)]),
            "total_runs": new_total_runs,
            "total_balls": new_total_balls,
            "total_fours": new_total_fours,
            "total_sixes": new_total_sixes,
            "total_matches": new_total_matches,
            "highest_score": new_highest,
            "last_active": datetime.now()
        })
    
    # Save match record
    await db.save_solo_match({
        "user_id": user_id,
        "user_name": game["user_name"],
        "runs": game["runs"],
        "balls": game["balls"],
        "fours": game["fours"],
        "sixes": game["sixes"],
        "ball_sequence": game["ball_sequence"],
        "created_at": datetime.now()
    })


async def solo_stats_command(client, message: Message):
    """Show solo player statistics"""
    user_id = message.from_user.id
    
    player = await db.get_solo_player(user_id)
    
    if not player:
        await message.reply_text(
            "📊 **No stats found!**\n\n"
            "Play your first solo match with /solo_start"
        )
        return
    
    strike_rate = (player.get("total_runs", 0) / max(player.get("total_balls", 1), 1)) * 100
    
    stats_text = f"""
📊 **{player.get('icon', '🏏')} {player.get('name', 'Player')}'s STATS**

━━━━━━━━━━━━━━━━━
🏏 **Matches:** {player.get('total_matches', 0)}
📈 **Total Runs:** {player.get('total_runs', 0)}
🎯 **Total Balls:** {player.get('total_balls', 0)}
⚡ **Strike Rate:** {strike_rate:.2f}
🏆 **Highest Score:** {player.get('highest_score', 0)}
🔴 **Fours:** {player.get('total_fours', 0)}
🟢 **Sixes:** {player.get('total_sixes', 0)}
━━━━━━━━━━━━━━━━━
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Play Again", callback_data="solo_start", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("◀️ BACK", callback_data="solo_back", style=ButtonStyle.DEFAULT)]
    ])
    
    await message.reply_text(stats_text, reply_markup=buttons)


async def solo_leaderboard_command(client, message: Message):
    """Show solo leaderboard"""
    players = await db.get_all_solo_players(limit=20)
    
    if not players:
        await message.reply_text("📊 **No players found!**\n\nBe the first to play solo mode!")
        return
    
    leaderboard_text = "🏆 **SOLO LEADERBOARD** 🏆\n\n"
    
    for i, player in enumerate(players[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard_text += f"{medal} {player.get('icon', '🏏')} **{player.get('name', 'Unknown')}** - {player.get('total_runs', 0)} runs\n"
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Play Solo", callback_data="solo_start", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("◀️ BACK", callback_data="solo_back", style=ButtonStyle.DEFAULT)]
    ])
    
    await message.reply_text(leaderboard_text, reply_markup=buttons)


async def solo_tree_community(callback_query: CallbackQuery):
    """Show solo tree community - player list"""
    players = await db.get_all_solo_players(limit=50)
    
    if not players:
        await callback_query.message.edit_text(
            "🌳 **SOLO TREE COMMUNITY**\n\n"
            "No solo players yet!\n\n"
            "Be the first to join with /solo_start"
        )
        await callback_query.answer()
        return
    
    # Format player list like screenshot
    player_list = "🌳 **SOLO TREE COMMUNITY**\n\n"
    player_list += "**Solo Players**\n\n"
    
    for i, player in enumerate(players[:20], 1):
        ball_seq = player.get("ball_sequences", [])
        if ball_seq and len(ball_seq) > 0:
            seq_str = ", ".join(str(s) for s in ball_seq[-6:])
        else:
            seq_str = "No balls yet"
        
        player_list += f"{i}. {player.get('icon', '🏏')} **{player.get('name', 'Unknown')}** = {player.get('total_runs', 0)}({player.get('total_balls', 0)})\n"
        player_list += f"   • 4s: {player.get('total_fours', 0):02d}, 6s: {player.get('total_sixes', 0):02d}\n"
        player_list += f"   • ID: `{player.get('user_id')}`\n"
        player_list += f"   • ({seq_str})\n\n"
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Join Solo", callback_data="solo_start", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)]
    ])
    
    await callback_query.message.edit_text(player_list[:4000], reply_markup=buttons)
    await callback_query.answer()


async def solo_play_callback(callback_query: CallbackQuery):
    """Solo play callback"""
    await solo_play_command(callback_query._client, callback_query.message)
    await callback_query.answer()


async def solo_end_match_callback(callback_query: CallbackQuery):
    """End solo match callback"""
    user_id = callback_query.from_user.id
    
    if user_id in solo_games:
        game = solo_games[user_id]
        await save_solo_match_result(user_id, game)
        del solo_games[user_id]
        
        await callback_query.message.edit_text(
            f"🏆 **MATCH ENDED!** 🏆\n\n"
            f"📊 **Final Score:** {game['runs']}/{game['wickets']}\n"
            f"📈 **Balls Faced:** {game['balls']}\n"
            f"🔴 **Fours:** {game['fours']}\n"
            f"🟢 **Sixes:** {game['sixes']}\n\n"
            f"Thanks for playing! 🎉"
        )
    else:
        await callback_query.message.edit_text("❌ No active solo game found!")
    
    await callback_query.answer()
