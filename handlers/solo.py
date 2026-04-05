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
solo_multi_players = {}  # Store multi-player games by chat_id

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
    """Start a solo match - Single player in DM, Multi-player in Group"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chat_id = message.chat.id
    chat_type = message.chat.type
    
    # In DM (Private) - Single player mode
    if chat_type == "private":
        await solo_start_single(client, message, user_id, user_name, chat_id)
        return
    
    # In Group - Multi-player mode
    if chat_type in ["group", "supergroup"]:
        await solo_start_multi(client, message, user_id, user_name, chat_id)
        return


async def solo_start_single(client, message, user_id, user_name, chat_id):
    """Single player solo mode (DM)"""
    if user_id in solo_games:
        await message.reply_text("❌ You already have an active solo game! Finish it first.")
        return
    
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
        "max_balls_per_bowler": 6,
        "total_bowlers": 3,
        "current_bowler": SOLO_BOWLERS[0],
        "bowler_number": None,
        "batter_number": None,
        "mode": "single",
        "created_at": datetime.now()
    }
    
    await create_or_get_player(user_id, user_name)
    first_bowler = SOLO_BOWLERS[0]
    
    await message.reply_text(
        f"🏏 **SOLO MATCH STARTED!**\n\n"
        f"👤 **Player:** {user_name}\n"
        f"🎯 **3 Bowlers:** {SOLO_BOWLERS[0]['icon']} {SOLO_BOWLERS[0]['name']}, {SOLO_BOWLERS[1]['icon']} {SOLO_BOWLERS[1]['name']}, {SOLO_BOWLERS[2]['icon']} {SOLO_BOWLERS[2]['name']}\n\n"
        f"📊 **Format:** 18 balls\n"
        f"⚡ **First Bowler:** {first_bowler['icon']} {first_bowler['name']}\n\n"
        f"Send numbers **1-6** on bot PM to play!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏏 Play Ball", callback_data="solo_play_ball", style=ButtonStyle.PRIMARY)],
            [InlineKeyboardButton("❌ End Match", callback_data="solo_end_match", style=ButtonStyle.DANGER)]
        ])
    )


async def solo_start_multi(client, message, user_id, user_name, chat_id):
    """Multi-player solo mode (Group) - Elimination style"""
    
    # Check if game already exists in this group
    if chat_id in solo_multi_players:
        game = solo_multi_players[chat_id]
        if game["status"] == "waiting":
            # Already a game waiting for players
            if user_id in [p["user_id"] for p in game["players"]]:
                await message.reply_text("❌ You already joined this game!")
                return
            game["players"].append({"user_id": user_id, "name": user_name, "runs": 0, "balls": 0, "status": "waiting"})
            await message.reply_text(f"✅ **{user_name} joined the game!** ({len(game['players'])} players)")
            
            # Update game message
            players_list = "\n".join([f"• {p['name']}" for p in game["players"]])
            await client.edit_message_text(
                chat_id,
                game["message_id"],
                f"🏏 **SOLO TOURNAMENT!**\n\n"
                f"**Players joined:**\n{players_list}\n\n"
                f"Type `/solo_start` to join!\n"
                f"Game will start in 60 seconds or when host clicks Start!"
            )
            return
    
    # Check if user is host and game exists
    if chat_id in solo_multi_players and solo_multi_players[chat_id]["status"] == "waiting":
        game = solo_multi_players[chat_id]
        if game["host_id"] == user_id:
            # Host is starting the game
            if len(game["players"]) < 2:
                await message.reply_text("❌ Need at least 2 players to start the game!")
                return
            
            game["status"] = "playing"
            game["current_player_index"] = 0
            await start_multi_player_turn(client, chat_id)
            return
    
    # Create new multi-player game
    solo_multi_players[chat_id] = {
        "host_id": user_id,
        "host_name": user_name,
        "players": [{"user_id": user_id, "name": user_name, "runs": 0, "balls": 0, "status": "playing"}],
        "status": "waiting",
        "current_player_index": 0,
        "message_id": None,
        "created_at": datetime.now()
    }
    
    msg = await message.reply_text(
        f"🏏 **SOLO TOURNAMENT STARTED!**\n\n"
        f"👤 **Host:** {user_name}\n"
        f"📊 **Players joined:** 1\n\n"
        f"Type `/solo_start` to join the game!\n"
        f"Host will start the game when ready.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Start Game", callback_data="solo_multi_start", style=ButtonStyle.SUCCESS)],
            [InlineKeyboardButton("❌ Cancel", callback_data="solo_multi_cancel", style=ButtonStyle.DANGER)]
        ])
    )
    solo_multi_players[chat_id]["message_id"] = msg.id


async def start_multi_player_turn(client, chat_id):
    """Start next player's turn in multi-player game"""
    game = solo_multi_players[chat_id]
    current_index = game["current_player_index"]
    
    if current_index >= len(game["players"]):
        # Game over - declare winner
        winner = max(game["players"], key=lambda x: x["runs"])
        await client.send_message(
            chat_id,
            f"🏆 **TOURNAMENT ENDED!** 🏆\n\n"
            f"🥇 **WINNER:** {winner['name']} with {winner['runs']} runs!\n\n"
            f"📊 **Final Scores:**\n" + "\n".join([f"• {p['name']}: {p['runs']} runs" for p in game["players"]]),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 New Tournament", callback_data="solo_multi_new", style=ButtonStyle.SUCCESS)]
            ])
        )
        del solo_multi_players[chat_id]
        return
    
    current_player = game["players"][current_index]
    
    # Create solo game for this player
    solo_games[current_player["user_id"]] = {
        "user_id": current_player["user_id"],
        "user_name": current_player["name"],
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
        "max_balls_per_bowler": 6,
        "total_bowlers": 3,
        "current_bowler": SOLO_BOWLERS[0],
        "bowler_number": None,
        "batter_number": None,
        "mode": "multi",
        "multi_chat_id": chat_id,
        "created_at": datetime.now()
    }
    
    await client.send_message(
        chat_id,
        f"🏏 **{current_player['name']}'s TURN!**\n\n"
        f"⚡ **Bowler:** {SOLO_BOWLERS[0]['icon']} {SOLO_BOWLERS[0]['name']}\n"
        f"Send numbers **1-6** on bot PM to play!\n"
        f"Type **W** for wicket!\n\n"
        f"⏰ You have 60 seconds!"
    )
    
    # Start timer for this player
    asyncio.create_task(multi_player_timer(client, chat_id, current_player["user_id"], current_player["name"]))


async def multi_player_timer(client, chat_id, user_id, player_name):
    """60 second timer for multi-player turn"""
    await asyncio.sleep(60)
    
    if chat_id in solo_multi_players:
        game = solo_multi_players[chat_id]
        current_index = game["current_player_index"]
        if current_index < len(game["players"]) and game["players"][current_index]["user_id"] == user_id:
            # Player timed out - eliminate
            await client.send_message(
                chat_id,
                f"⏰ **{player_name} timed out! Eliminated from the game!**"
            )
            game["players"].pop(current_index)
            await start_multi_player_turn(client, chat_id)


async def create_or_get_player(user_id, user_name):
    """Create or get solo player stats"""
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
        f"🎯 **Balls left this bowler:** {balls_left_this_bowler}\n\n"
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
    
    bowler_num = game.get("bowler_number", random.randint(1, 6))
    game["batter_number"] = number
    
    # CHECK IF OUT (Numbers match)
    if bowler_num == number:
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
            # If multi-player mode, move to next player
            if game.get("mode") == "multi":
                await handle_multi_player_elimination(user_id, game)
        else:
            if game["current_ball"] % game["max_balls_per_bowler"] == 0:
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
    
    if not is_match_over and game["current_ball"] % game["max_balls_per_bowler"] == 0:
        next_bowler_index = game["current_bowler_index"] + 1
        if next_bowler_index < game["total_bowlers"]:
            game["current_bowler_index"] = next_bowler_index
            game["current_bowler"] = SOLO_BOWLERS[next_bowler_index]
            result["next_bowler"] = game["current_bowler"]
    
    if is_match_over:
        await save_solo_match_result(user_id, game)
        solo_games[user_id]["status"] = "completed"
        if game.get("mode") == "multi":
            await handle_multi_player_completion(user_id, game)
    
    return result


async def handle_multi_player_elimination(user_id, game):
    """Handle player elimination in multi-player mode"""
    chat_id = game.get("multi_chat_id")
    if chat_id and chat_id in solo_multi_players:
        multi_game = solo_multi_players[chat_id]
        current_index = multi_game["current_player_index"]
        
        # Update player's score
        for p in multi_game["players"]:
            if p["user_id"] == user_id:
                p["runs"] = game["runs"]
                p["status"] = "eliminated"
                break
        
        # Move to next player
        multi_game["current_player_index"] = current_index + 1
        await start_multi_player_turn(callback_query._client, chat_id)


async def handle_multi_player_completion(user_id, game):
    """Handle player completing all balls in multi-player mode"""
    chat_id = game.get("multi_chat_id")
    if chat_id and chat_id in solo_multi_players:
        multi_game = solo_multi_players[chat_id]
        current_index = multi_game["current_player_index"]
        
        # Update player's score
        for p in multi_game["players"]:
            if p["user_id"] == user_id:
                p["runs"] = game["runs"]
                p["status"] = "completed"
                break
        
        # Move to next player
        multi_game["current_player_index"] = current_index + 1
        await start_multi_player_turn(callback_query._client, chat_id)


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
    
    await db.save_solo_match({
        "user_id": user_id,
        "user_name": game["user_name"],
        "runs": game["runs"],
        "balls": game["balls"],
        "fours": game["fours"],
        "sixes": game["sixes"],
        "ball_sequence": game["ball_sequence"],
        "chat_id": game.get("chat_id"),
        "mode": game.get("mode", "single"),
        "created_at": datetime.now()
    })


async def solo_stats_command(client, message: Message):
    """Show solo player statistics"""
    user_id = message.from_user.id
    
    player = await db.get_solo_player(user_id)
    
    if not player:
        await message.reply_text("📊 **No stats found!**\n\nPlay your first solo match with /solo_start")
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
        await callback_query.message.edit_text("🌳 **SOLO TREE COMMUNITY**\n\nNo solo players yet!\n\nBe the first to join with /solo_start")
        await callback_query.answer()
        return
    
    player_list = "🌳 **SOLO TREE COMMUNITY**\n\n**Solo Players**\n\n"
    
    for i, player in enumerate(players[:20], 1):
        ball_seq = player.get("ball_sequences", [])
        seq_str = ", ".join(str(s) for s in ball_seq[-6:]) if ball_seq else "No balls yet"
        
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
    await solo_play_command(callback_query._client, callback_query.message)
    await callback_query.answer()


async def solo_end_match_callback(callback_query: CallbackQuery):
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


async def solo_multi_start_callback(callback_query: CallbackQuery):
    """Start multi-player game from button"""
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    
    if chat_id in solo_multi_players:
        game = solo_multi_players[chat_id]
        if game["host_id"] == user_id:
            if len(game["players"]) < 2:
                await callback_query.answer("Need at least 2 players!", show_alert=True)
                return
            game["status"] = "playing"
            game["current_player_index"] = 0
            await start_multi_player_turn(callback_query._client, chat_id)
            await callback_query.answer("Game started!")
        else:
            await callback_query.answer("Only host can start the game!", show_alert=True)
    else:
        await callback_query.answer("No game found!", show_alert=True)


async def solo_multi_cancel_callback(callback_query: CallbackQuery):
    """Cancel multi-player game"""
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    
    if chat_id in solo_multi_players:
        game = solo_multi_players[chat_id]
        if game["host_id"] == user_id:
            del solo_multi_players[chat_id]
            await callback_query.message.edit_text("❌ Tournament cancelled!")
        else:
            await callback_query.answer("Only host can cancel!", show_alert=True)
    await callback_query.answer()


async def solo_multi_new_callback(callback_query: CallbackQuery):
    """Start new tournament"""
    await callback_query.message.delete()
    await callback_query.answer()
