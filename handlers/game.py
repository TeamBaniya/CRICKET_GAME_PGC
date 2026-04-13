from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from datetime import datetime, timedelta
import asyncio
from config import MEMBERS_LIST_IMAGE_URL, BOT_USERNAME, BOWLING_VIDEO_URL

active_games = {}

async def create_game_command(client, message: Message):
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Solo", callback_data="create_solo", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("👥 Team", callback_data="create_team", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("◀️ BACK", callback_data="back_to_main", style=ButtonStyle.DEFAULT)
        ]
    ])
    await message.reply_text("🎮 **Create Game**\n\nChoose game type:", reply_markup=buttons)

async def create_solo_game(callback_query):
    chat_id = callback_query.message.chat.id
    user = callback_query.from_user
    
    active_games[chat_id] = {
        "type": "solo",
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=2),
        "players": [{"user_id": user.id, "name": user.first_name, "player_number": 1, "first_name": user.first_name, "username": user.username}],
        "status": "waiting",
        "host_id": user.id,
        "message_id": callback_query.message.id,
        "current_runs": 0,
        "current_wickets": 0,
        "current_balls": 0,
        "total_balls": 12,
        "ball_sequence": []
    }
    
    await callback_query.message.edit_text(
        f"🎉 **Solo Game Created!** 🎉\n\n"
        f"👤 **Host:** {user.first_name}\n"
        f"👥 **Players joined:** 1\n\n"
        f"Join the game using `/joingame` (2 minutes to join)\n\n"
        f"⏰ You have 2 minutes to join!\n\n"
        f"Game will start automatically when timer ends!"
    )
    
    await start_timers(callback_query._client, chat_id)
    await callback_query.answer()

async def create_team_game(callback_query):
    await callback_query.message.edit_text("👥 Team Game Coming Soon!")
    await callback_query.answer()

async def joingame_command(client, message: Message):
    if not message.from_user:
        await message.reply_text("❌ Anonymous users cannot join!")
        return
    
    user = message.from_user
    chat_id = message.chat.id
    
    if chat_id not in active_games:
        await message.reply_text(f"😎 {user.first_name}, no game found! Start a new game with /create_game")
        return
    
    game = active_games[chat_id]
    if game["status"] != "waiting":
        await message.reply_text(f"🟢 {user.first_name}, the game is not in the joining state!")
        return
    
    if user.id in [p["user_id"] for p in game["players"]]:
        await message.reply_text(f"✅ {user.first_name}, you already joined the game!")
        return
    
    player_number = len(game["players"]) + 1
    game["players"].append({
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "player_number": player_number
    })
    
    await message.reply_text(f"🏏️ {user.first_name}, you've joined the game! (Player {player_number}) 🏏️")
    await update_game_message(client, chat_id, game)

async def update_game_message(client, chat_id, game):
    players_list = "\n".join([f"  {p['player_number']}. {p['first_name']}" for p in game["players"]])
    time_left = (game["expires_at"] - datetime.now()).seconds
    minutes = time_left // 60
    seconds = time_left % 60
    
    try:
        await client.edit_message_text(
            chat_id,
            game["message_id"],
            f"🎉 **Game Created!** 🎉\n\n"
            f"Join the game using `/joingame` ({minutes}:{seconds:02d} minutes left)\n\n"
            f"**Players joined:**\n{players_list}\n\n"
            f"**Total players:** {len(game['players'])}\n\n"
            f"Game will start automatically when timer ends!"
        )
    except:
        pass

async def start_timers(client, chat_id):
    await asyncio.sleep(60)
    if chat_id in active_games and active_games[chat_id]["status"] == "waiting":
        await client.send_message(chat_id, "⏰ **60 seconds left! Join quickly using /joingame**")
    
    await asyncio.sleep(30)
    if chat_id in active_games and active_games[chat_id]["status"] == "waiting":
        await client.send_message(chat_id, "⚠️ **30 seconds left only, /joingame !!**")
    
    await asyncio.sleep(20)
    if chat_id in active_games and active_games[chat_id]["status"] == "waiting":
        await client.send_message(chat_id, "⏰ **Last 10 seconds left only, /joingame !!**")
    
    await asyncio.sleep(10)
    await auto_start_game(client, chat_id)

async def auto_start_game(client, chat_id):
    if chat_id not in active_games:
        return
    
    game = active_games[chat_id]
    if game["status"] != "waiting":
        return
    
    game["status"] = "live"
    
    players_list = ""
    for i, player in enumerate(game["players"], 1):
        username = f"@{player['username']}" if player.get('username') else player['first_name']
        players_list += f"{i}. {username}\n"
    
    caption = f"🏏 **CRICKET GAME PLAYERS**\n🌳 **SOLO TREE COMMUNITY**\n\n**Unknown Host**\n**Solo Players**\n\n{players_list}"
    
    if MEMBERS_LIST_IMAGE_URL:
        await client.send_photo(chat_id, photo=MEMBERS_LIST_IMAGE_URL, caption=caption)
    else:
        await client.send_message(chat_id, caption)
    
    players = game["players"]
    game["current_bowler_index"] = 0
    game["current_batter_index"] = 1 if len(players) > 1 else 0
    game["current_bowler"] = players[0]["user_id"]
    game["current_batter"] = players[game["current_batter_index"]]["user_id"]
    game["bowler_name"] = players[0]["first_name"]
    game["bowling_status"] = "waiting_for_number"
    game["batting_status"] = "waiting"
    
    await send_bowling_screen(client, chat_id, game["bowler_name"])

async def send_bowling_screen(client, chat_id, bowler_name):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 Bowling", url=f"https://t.me/{BOT_USERNAME}?start=bowling_{chat_id}", style=ButtonStyle.PRIMARY)]
    ])
    
    await client.send_message(chat_id, f"🎯 **Hey {bowler_name}, now you're bowling!**")
    await asyncio.sleep(2)
    
    if BOWLING_VIDEO_URL:
        await client.send_video(chat_id, BOWLING_VIDEO_URL, caption=f"👏 **{bowler_name} click below to send your number!**", reply_markup=buttons)
    else:
        await client.send_message(chat_id, f"👏 **{bowler_name} click below to send your number!**", reply_markup=buttons)
        
