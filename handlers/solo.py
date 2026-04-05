# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ButtonStyle
from database import db
from datetime import datetime
import random
import asyncio

# Store active solo games (user_id based - works in both DM and Group)
solo_games = {}
solo_timers = {}

# Solo player icons
SOLO_ICONS = ["🟢", "⚽", "🔥", "🌞", "💬", "🎮", "🏀", "🐍", "🕊️", "⭐", "⚡", "💎"]

# 3 Bowlers for solo mode
SOLO_BOWLERS = [
    {"name": "Fast Bowler", "icon": "⚡", "speed": "FAST"},
    {"name": "Spin Bowler", "icon": "🔄", "speed": "SPIN"},
    {"name": "Pace Bowler", "icon": "💨", "speed": "PACE"}
]


async def solo_play_command(client, message: Message):
    """Solo play command - Show solo mode menu (works in DM and Group)"""
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
        "Play cricket matches against 3 different bowlers!\n\n"
        "• **Start Solo Match** - Play a new match\n"
        "• **My Stats** - View your statistics\n"
        "• **Leaderboard** - Top players list\n\n"
        "Send numbers **1-6** on bot PM to play your shots!\n"
        "Type **W** for wicket!",
        reply_markup=buttons
    )


async def solo_start_command(client, message: Message):
    """Start a solo match with 3 bowlers (works in DM and Group)"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chat_id = message.chat.id
    
    # Check if already in game
    if user_id in solo_games:
        await message.reply_text("❌ You already have an active solo game! Finish it first.")
        return
    
    # Create new solo game with 3 bowlers
    solo_games[user_id] = {
        "user_id": user_id,
        "user_name": user_name,
        "chat_id": chat_id,
        "runs": 0,
        "balls": 0,
        "wickets": 0,
        "fours": 0,
        "sixes": 0,
        "ball_sequence": [],
        "status": "batting",
        "current_ball": 0,
        "current_bowler_index": 0,
        "max_balls_per_bowler": 6,  # 6 balls per bowler
        "total_bowlers": 3,
        "current_bowler": SOLO_BOWLERS[0],
        "bowler_number": None,
        "batter_number": None,
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
    
    # Show first bowler
    first_bowler = SOLO_BOWLERS[0]
    
    await message.reply_text(
        f"🏏 **SOLO MATCH STARTED!**\n\n"
        f"👤 **Player:** {user_name}\n"
        f"📍 **Chat:** {'Group' if message.chat.type in ['group', 'supergroup'] else 'Private'}\n"
        f"🎯 **You will face 3 bowlers:**\n"
        f"   {SOLO_BOWLERS[0]['icon']} {SOLO_BOWLERS[0]['name']}\n"
        f"   {SOLO_BOWLERS[1]['icon']} {SOLO_BOWLERS[1]['name']}\n"
        f"   {SOLO_BOWLERS[2]['icon']} {SOLO_BOWLERS[2]['name']}\n\n"
        f"📊 **Format:** 3 bowlers × 6 balls = 18 balls\n\n"
        f"🎯 **Ratings:** ND BAT | MENTAL 66 | PACE 63 | PHYSICAL 66\n\n"
        f"⚡ **First Bowler:** {first_bowler['icon']} {first_bowler['name']}\n\n"
        f"Send numbers **1-6** on bot PM to play your shots!\n"
        f"Type **W** for wicket!\n\n"
        f"Click **Play Ball** to start!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏏 Play Ball", callback_data="solo_play_ball", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("❌ End Match", callback_data="solo_end_match", style=ButtonStyle.DANGER)]
        ])
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
    
    current_bowler = game["current_bowler"]
    balls_this_bowler = game["current_ball"] % game["max_balls_per_bowler"]
    balls_left_this_bowler = game["max_balls_per_bowler"] - balls_this_bowler
    
    await callback_query.message.edit_text(
        f"🏏 **PLAY BALL!**\n\n"
        f"⚡ **Current Bowler:** {current_bowler['icon']} {current_bowler['name']}\n"
        f"📊 **Score:** {game['runs']}/{game['wickets']}\n"
        f"📈 **Balls:** {game['current_ball']}/{game['total_bowlers'] * game['max_balls_per_bowler']}\n"
        f"🎯 **Balls left this bowler:** {balls_left_this_bowler}\n"
        f"🎯 **Ratings:** ND BAT | MENTAL 66 | PACE 63 | PHYSICAL 66\n\n"
        f"**Send number (1-6) on bot PM!**"
    )
    await callback_query.answer()


async def solo_play_number(user_id: int, number: int):
    """Process solo play number with OUT logic"""
    if user_id not in solo_games:
        return None
    
    game = solo_games[user_id]
    
    if game["status"] != "batting":
        return None
    
    # Get bowler's number (store previous or random)
    bowler_num = game.get("bowler_number", random.randint(1, 6))
    game["batter_number"] = number
    
    # CHECK IF OUT (Numbers match)
    if bowler_num == number:
        # WICKET!
        game["wickets"] += 1
        game["balls"] += 1
        game["current_ball"] += 1
        game["ball_sequence"].append("W")
        
        is_match_over = game["current_ball"] >= (game["total_bowlers"] * game["max_balls_per_bowler"]) or game["wickets"] >= 10
        
        result = {
            "is_wicket": True,
            "runs": 0,
            "is_match_over": is_match_over,
            "current_score": f"{game['runs']}/{game['wickets']}",
            "balls_left": (game["total_bowlers"] * game["max_balls_per_bowler"]) - game["current_ball"],
            "bowler_num": bowler_num,
            "batter_num": number
        }
        
        if is_match_over:
            await save_solo_match_result(user_id, game)
            solo_games[user_id]["status"] = "completed"
        else:
            # Check if bowler's 6 balls are over
            if game["current_ball"] % game["max_balls_per_bowler"] == 0:
                # Switch to next bowler
                next_bowler_index = game["current_bowler_index"] + 1
                if next_bowler_index < game["total_bowlers"]:
                    game["current_bowler_index"] = next_bowler_index
                    game["current_bowler"] = SOLO_BOWLERS[next_bowler_index]
                    game["bowler_number"] = None
        
        return result
    
    # NOT OUT - Add runs
    runs = number
    game["runs"] += runs
    game["balls"] += 1
    game["current_ball"] += 1
    game["ball_sequence"].append(runs)
    
    if runs == 4:
        game["fours"] += 1
    elif runs == 6:
        game["sixes"] += 1
    
    # Clear bowler number for next ball (new random each ball)
    game["bowler_number"] = None
    
    is_match_over = game["current_ball"] >= (game["total_bowlers"] * game["max_balls_per_bowler"]) or game["wickets"] >= 10
    
    result = {
        "is_wicket": False,
        "runs": runs,
        "is_match_over": is_match_over,
        "current_score": f"{game['runs']}/{game['wickets']}",
        "balls_left": (game["total_bowlers"] * game["max_balls_per_bowler"]) - game["current_ball"],
        "fours": game["fours"],
        "sixes": game["sixes"],
        "bowler_num": bowler_num,
        "batter_num": number
    }
    
    # Check if bowler's 6 balls are over and not match over
    if not is_match_over and game["current_ball"] % game["max_balls_per_bowler"] == 0:
        # Switch to next bowler
        next_bowler_index = game["current_bowler_index"] + 1
        if next_bowler_index < game["total_bowlers"]:
            game["current_bowler_index"] = next_bowler_index
            game["current_bowler"] = SOLO_BOWLERS[next_bowler_index]
            result["next_bowler"] = game["current_bowler"]
    
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
    
    is_match_over = game["current_ball"] >= (game["total_bowlers"] * game["max_balls_per_bowler"]) or game["wickets"] >= 10
    
    result = {
        "is_wicket": True,
        "is_match_over": is_match_over,
        "current_score": f"{game['runs']}/{game['wickets']}",
        "balls_left": (game["total_bowlers"] * game["max_balls_per_bowler"]) - game["current_ball"]
    }
    
    if is_match_over:
        await save_solo_match_result(user_id, game)
        solo_games[user_id]["status"] = "completed"
    
    return result


async def save_solo_match_result(user_id: int, game: dict):
    """Save solo match result to database"""
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
        "chat_id": game.get("chat_id"),
        "created_at": datetime.now()
    })


async def solo_stats_command(client, message: Message):
    """Show solo player statistics (works in DM and Group)"""
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
    """Show solo leaderboard (works in DM and Group)"""
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
