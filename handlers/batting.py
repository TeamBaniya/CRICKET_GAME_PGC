# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ButtonStyle
from config import BATTING_RATINGS, BATTING_VIDEO_URL, SIX_VIDEO_URL, FOUR_VIDEO_URL, OUT_VIDEO_URL
import random

# Store batting sessions
batting_sessions = {}

async def batting_command(client, message: Message):
    """/batting command - Play as batsman"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    args = message.text.split()
    
    # Check if user is the current batsman
    from handlers.gameplay import active_games
    if chat_id not in active_games:
        await message.reply_text("❌ No active game found! Use /startgame first.")
        return
    
    game = active_games[chat_id]
    if game.get("current_batter") != user_id:
        await message.reply_text("❌ You are not the current batsman!")
        return
    
    if len(args) < 2:
        # Show batting ratings
        ratings_text = " | ".join([f"{k} {v}" for k, v in BATTING_RATINGS.items()])
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1", callback_data="bat_1", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("2", callback_data="bat_2", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("3", callback_data="bat_3", style=ButtonStyle.PRIMARY)
            ],
            [
                InlineKeyboardButton("4", callback_data="bat_4", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("5", callback_data="bat_5", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("6", callback_data="bat_6", style=ButtonStyle.PRIMARY)
            ],
            [
                InlineKeyboardButton("🎯 TIMING", callback_data="timing", style=ButtonStyle.SUCCESS),
                InlineKeyboardButton("🎯 DIRECTION", callback_data="direction", style=ButtonStyle.SUCCESS)
            ]
        ])
        
        await message.reply_text(
            f"🏏 **Now Batter: {message.from_user.first_name}**\n\n"
            f"📊 **Ratings:** {ratings_text}\n\n"
            f"🎯 **Choose your shot:**\n"
            f"• Click number button (1-6)\n"
            f"• Or use /batting <number>\n\n"
            f"Example: /batting 4",
            reply_markup=buttons
        )
        return
    
    try:
        number = int(args[1])
        if number not in range(1, 7):
            raise ValueError
        await process_batting_number(client, chat_id, user_id, number, message)
    except ValueError:
        await message.reply_text("❌ Please send a number between 1-6!")


async def process_batting_number(client, chat_id, user_id, number, message=None):
    """Process batting number and calculate result"""
    from handlers.gameplay import active_games, bowler_number_store
    from handlers.dm_handler import end_match_team, switch_to_next_batsman_team
    
    if chat_id not in active_games:
        if message:
            await message.reply_text("❌ No active game found!")
        return
    
    game = active_games[chat_id]
    bowler_num = bowler_number_store.get(chat_id, random.randint(1, 6))
    
    # Send batting video
    if BATTING_VIDEO_URL:
        await client.send_video(chat_id, BATTING_VIDEO_URL, caption=f"🏏 **{message.from_user.first_name} is batting!**")
    
    # CHECK IF OUT (Numbers match)
    if bowler_num == number:
        # WICKET!
        game["current_wickets"] = game.get("current_wickets", 0) + 1
        game["current_balls"] = game.get("current_balls", 0) + 1
        
        # Send OUT video
        if OUT_VIDEO_URL:
            await client.send_video(chat_id, OUT_VIDEO_URL, caption=f"🎯 **Number matches! {message.from_user.first_name} is out!**")
        else:
            await client.send_message(chat_id, f"🎯 **Number matches! {message.from_user.first_name} is out!**")
        
        response_time = random.randint(30, 150)
        await client.send_message(
            chat_id,
            f"📊 **Score:** {game['current_runs']}/{game['current_wickets']}\n"
            f"📈 **Balls:** {game['current_balls']}/{(game.get('total_overs', 2) * 6)}\n"
            f"⏱️ {response_time}ms\n\n"
            f"❌ Bowler: {bowler_num} | Batter: {number}\n"
            f"**OUT!**"
        )
        
        if message:
            await message.reply_text(f"❌ **YOU'RE OUT!** Bowler's number was {bowler_num}")
        
        # Clear stored number
        bowler_number_store[chat_id] = 0
        
        # Check match end
        if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
            await end_match_team(client, chat_id, game)
        else:
            # Switch to next batsman
            await switch_to_next_batsman_team(client, chat_id, game)
        return
    
    # NOT OUT - Add runs
    runs = number
    game["current_runs"] = game.get("current_runs", 0) + runs
    game["current_balls"] = game.get("current_balls", 0) + 1
    game["ball_sequence"].append(runs)
    game["batting_status"] = "waiting_for_bowler"
    
    # Send runs video
    if runs == 6 and SIX_VIDEO_URL:
        await client.send_video(chat_id, SIX_VIDEO_URL, caption=f"🎯 **SIX!** 🚀")
    elif runs == 4 and FOUR_VIDEO_URL:
        await client.send_video(chat_id, FOUR_VIDEO_URL, caption=f"🎯 **FOUR!** 💥")
    
    response_time = random.randint(30, 150)
    await client.send_message(
        chat_id,
        f"🏏 **{runs} RUN{'S' if runs > 1 else ''}!**\n\n"
        f"📊 **Score:** {game['current_runs']}/{game['current_wickets']}\n"
        f"📈 **Balls:** {game['current_balls']}/{(game.get('total_overs', 2) * 6)}\n"
        f"⏱️ {response_time}ms\n\n"
        f"Bowler: {bowler_num} | Batter: {number}\n"
        f"🏏 **{runs} RUNS!**"
    )
    
    if message:
        await message.reply_text(f"✅ You sent {number}! {runs} runs added!")
    
    # Clear stored number for next ball
    bowler_number_store[chat_id] = 0
    
    # Check match end
    if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
        await end_match_team(client, chat_id, game)
    else:
        # Next ball - ask bowler for number
        game["bowling_status"] = "waiting_for_number"
        game["batting_status"] = "waiting_for_number"
        
        # Switch to next bowler
        players = game.get("players", [])
        current_bowler_index = game.get("current_bowler_index", 0)
        next_bowler_index = (current_bowler_index + 1) % len(players)
        next_bowler = players[next_bowler_index]
        
        game["current_bowler"] = next_bowler["user_id"]
        game["current_bowler_index"] = next_bowler_index
        
        await client.send_message(
            chat_id,
            f"🔄 **Next ball! Hey {next_bowler['first_name']}, send your number (1-6) on bot PM!**"
        )


async def batting_callback(callback_query: CallbackQuery):
    """Handle batting number button clicks"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    if data.startswith("bat_"):
        number = int(data.split("_")[1])
        
        # Create fake message for process_batting_number
        class FakeMessage:
            def __init__(self, from_user, reply_text):
                self.from_user = from_user
                self.reply_text = reply_text
        
        fake_msg = FakeMessage(callback_query.from_user, callback_query.message.reply_text)
        await process_batting_number(callback_query._client, chat_id, user_id, number, fake_msg)
        await callback_query.answer()
