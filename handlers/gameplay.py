# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from config import BOWLING_SPEEDS_BUTTONS, BATTING_RATINGS, BOWLING_VIDEO_URL, BATTING_VIDEO_URL, OUT_VIDEO_URL, SIX_VIDEO_URL, FOUR_VIDEO_URL
import random
import asyncio
from datetime import datetime

# Store active game sessions
active_games = {}
bowling_timers = {}
batting_timers = {}

# Store bowler and batter numbers
bowler_number_store = {}
batter_number_store = {}


# ==================== BOWLING COMMANDS ====================

async def bowling_command(client, message: Message):
    """/bowling command - Select bowler"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    args = message.text.split()
    
    # Check if user is the current bowler
    if chat_id not in active_games:
        await message.reply_text("❌ No active game found! Use /startgame first.")
        return
    
    game = active_games[chat_id]
    if game.get("current_bowler") != user_id:
        await message.reply_text("❌ You are not the current bowler!")
        return
    
    if len(args) < 2:
        # Show bowling speed buttons
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
        
        if BOWLING_VIDEO_URL:
            await client.send_video(
                chat_id,
                video=BOWLING_VIDEO_URL,
                caption=f"🎯 **Hey {message.from_user.first_name}, now you're bowling!**\n\nChoose your bowling speed:",
                reply_markup=buttons
            )
        else:
            await message.reply_text(
                f"🎯 **Hey {message.from_user.first_name}, now you're bowling!**\n\n"
                f"Choose your bowling speed:\n\nFAST | PHYSICAL | 63",
                reply_markup=buttons
            )
        return
    
    speed = args[1].upper()
    if speed not in ["FAST", "PHYSICAL", "63"]:
        await message.reply_text(
            f"❌ Invalid speed! Choose from: FAST, PHYSICAL, 63"
        )
        return
    
    # Save bowling selection
    game["selected_speed"] = speed
    game["bowling_status"] = "waiting_for_number"
    
    # Send bowling video
    if BOWLING_VIDEO_URL:
        await client.send_video(chat_id, BOWLING_VIDEO_URL, caption=f"🎯 **Speed {speed} selected!**\n\nNow send number on bot PM (1-6)\n⏰ You have 60 seconds!")
    else:
        await message.reply_text(
            f"✅ **Speed {speed} selected!**\n\n"
            f"Now send number on bot PM (1-6)\n"
            f"⏰ You have 60 seconds!"
        )
    
    # Start 60 second timer
    await start_bowling_timer(client, chat_id, message.from_user.first_name)


async def start_bowling_timer(client, chat_id, bowler_name):
    """60 second timer for bowler to send number"""
    for remaining in range(60, 0, -1):
        if chat_id not in active_games:
            return
        
        game = active_games[chat_id]
        if game.get("bowling_status") != "waiting_for_number":
            return
        
        if remaining == 30:
            await client.send_message(
                chat_id,
                f"⚠️ **Warning: {bowler_name}, you have 30 seconds left to send a number!**"
            )
        elif remaining == 10:
            await client.send_message(
                chat_id,
                f"⚠️ **Warning: {bowler_name}, you have 10 seconds left to send a number!**"
            )
        
        await asyncio.sleep(1)
    
    # Timeout - penalty
    if chat_id in active_games and active_games[chat_id].get("bowling_status") == "waiting_for_number":
        await client.send_message(
            chat_id,
            "⏰ **No message received from bowler, deducting 6 runs of bowler.**\n\n"
            "❌ **Seems Bowling player is not responding, User Eliminated from the game !!**"
        )
        
        # Switch to next bowler
        await switch_to_next_bowler(client, chat_id)


async def switch_to_next_bowler(client, chat_id):
    """Switch to next bowler after timeout or wicket"""
    if chat_id not in active_games:
        return
    
    game = active_games[chat_id]
    players = game.get("players", [])
    if not players:
        return
    
    current_index = game.get("current_bowler_index", 0)
    next_index = (current_index + 1) % len(players)
    next_bowler = players[next_index]
    
    game["current_bowler"] = next_bowler["user_id"]
    game["current_bowler_index"] = next_index
    game["bowling_status"] = "waiting_for_speed"
    
    await client.send_message(
        chat_id,
        f"🔄 **Hey {next_bowler['first_name']}, now you're bowling!**"
    )


async def bowling_speed_selected(callback_query, speed):
    """When bowler selects speed from inline button"""
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    if chat_id not in active_games:
        await callback_query.answer("No active game!", show_alert=True)
        return
    
    game = active_games[chat_id]
    if game.get("current_bowler") != user_id:
        await callback_query.answer("You are not the current bowler!", show_alert=True)
        return
    
    game["selected_speed"] = speed
    game["bowling_status"] = "waiting_for_number"
    
    await callback_query.message.edit_text(
        f"✅ **Speed {speed} selected!**\n\n"
        f"Now send number on bot PM (1-6)\n"
        f"⏰ You have 60 seconds!"
    )
    await callback_query.answer()
    
    # Start timer
    await start_bowling_timer(callback_query._client, chat_id, callback_query.from_user.first_name)


async def show_bowling_speed_options(callback_query):
    """Show bowling speed options in group"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("FAST", callback_data="bowl_speed_fast", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("PHYSICAL", callback_data="bowl_speed_physical", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("63", callback_data="bowl_speed_63", style=ButtonStyle.PRIMARY)
        ]
    ])
    
    await callback_query.message.edit_text(
        "🎯 **Choose your bowling speed:**",
        reply_markup=buttons
    )
    await callback_query.answer()


# ==================== BATTING COMMANDS ====================

async def batting_command(client, message: Message):
    """/batting command - Play as batsman"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    args = message.text.split()
    
    if chat_id not in active_games:
        await message.reply_text("❌ No active game found! Use /startgame first.")
        return
    
    game = active_games[chat_id]
    
    if len(args) < 2:
        ratings_text = " | ".join([f"{k} {v}" for k, v in BATTING_RATINGS.items()])
        await message.reply_text(
            f"🏏 **Now Batter can send number (1-6)!!**\n\n"
            f"📊 **Ratings:** {ratings_text}\n\n"
            f"Send number (1-6) to play the ball!\n"
            f"Example: /batting 4"
        )
        return
    
    try:
        number = int(args[1])
        if number not in range(1, 7):
            raise ValueError
    except ValueError:
        await message.reply_text("❌ Please send a number between 1-6!")
        return
    
    # Get bowler's number
    bowler_num = bowler_number_store.get(chat_id, 0)
    
    # Check if OUT (numbers match)
    if bowler_num == number and bowler_num != 0:
        # WICKET!
        game["current_wickets"] = game.get("current_wickets", 0) + 1
        game["current_balls"] = game.get("current_balls", 0) + 1
        
        # Send OUT video
        if OUT_VIDEO_URL:
            await client.send_video(chat_id, OUT_VIDEO_URL, caption=f"🎯 **Number matches! {message.from_user.first_name} is out!**")
        else:
            await message.reply_text(f"🎯 **Number matches! {message.from_user.first_name} is out!**")
        
        response_time = random.randint(30, 150)
        await message.reply_text(
            f"📊 Score: {game['current_runs']}/{game['current_wickets']}\n"
            f"⏱️ {response_time}ms\n\n"
            f"❌ {message.from_user.first_name} dismissed!"
        )
        
        # Check for match end
        if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
            await end_match(client, message, chat_id)
            return
        
        # Switch to next batsman
        await switch_to_next_batsman(client, chat_id)
        return
    
    # NOT OUT - Add runs
    runs = number
    game["current_runs"] = game.get("current_runs", 0) + runs
    game["current_balls"] = game.get("current_balls", 0) + 1
    game["ball_sequence"].append(runs)
    
    # Send runs video
    if runs == 6 and SIX_VIDEO_URL:
        await client.send_video(chat_id, SIX_VIDEO_URL, caption=f"🎯 **SIX!** 🚀")
    elif runs == 4 and FOUR_VIDEO_URL:
        await client.send_video(chat_id, FOUR_VIDEO_URL, caption=f"🎯 **FOUR!** 💥")
    elif BATTING_VIDEO_URL:
        await client.send_video(chat_id, BATTING_VIDEO_URL, caption=f"🏏 **{runs} RUN{'S' if runs > 1 else ''}!**")
    else:
        await message.reply_text(f"🏏 **{runs} RUN{'S' if runs > 1 else ''}!**")
    
    response_time = random.randint(30, 150)
    await message.reply_text(
        f"📊 Score: {game['current_runs']}/{game['current_wickets']}\n"
        f"📈 Balls: {game['current_balls']}/{(game.get('total_overs', 2) * 6)}\n"
        f"⏱️ {response_time}ms\n\n"
        f"Bowler: {bowler_num} | Batter: {number}"
    )
    
    # Clear stored numbers for next ball
    bowler_number_store[chat_id] = 0
    
    # Check for match end
    if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
        await end_match(client, message, chat_id)
        return
    
    # Next ball - ask bowler for number
    game["bowling_status"] = "waiting_for_number"
    game["batting_status"] = "waiting_for_number"
    
    await client.send_message(
        chat_id,
        f"🔄 **Next ball! Bowler, send your number (1-6) on bot PM!**"
    )


async def switch_to_next_batsman(client, chat_id):
    """Switch to next batsman after wicket"""
    if chat_id not in active_games:
        return
    
    game = active_games[chat_id]
    players = game.get("players", [])
    current_batter_index = game.get("current_batter_index", 0)
    next_index = current_batter_index + 1
    
    if next_index < len(players):
        next_batter = players[next_index]
        game["current_batter"] = next_batter["user_id"]
        game["current_batter_index"] = next_index
        game["batting_status"] = "waiting_for_number"
        
        await client.send_message(
            chat_id,
            f"🔄 **Hey {next_batter['first_name']}, now you're batting!**"
        )
    else:
        # No more batsmen - match over
        await end_match(client, None, chat_id)


async def show_batting_ratings(callback_query):
    """Show batting ratings in group"""
    ratings_text = " | ".join([f"{k} {v}" for k, v in BATTING_RATINGS.items()])
    
    await callback_query.message.edit_text(
        f"🏏 **Now Batter can send number (1-6)!!**\n\n"
        f"📊 **Ratings:** {ratings_text}"
    )
    await callback_query.answer()


async def timing_selected(callback_query):
    """TIMING button selected"""
    await callback_query.message.edit_text(
        "🎯 **TIMING SHOT SELECTED!**\n\n"
        "Send number on bot PM (1-6)\n"
        "Based on your timing, runs will be added!"
    )
    await callback_query.answer()


async def direction_selected(callback_query):
    """DIRECTION button selected"""
    await callback_query.message.edit_text(
        "🎯 **DIRECTION SHOT SELECTED!**\n\n"
        "Send number on bot PM (1-6)\n"
        "Based on your direction, runs will be added!"
    )
    await callback_query.answer()


async def take_run_selected(callback_query):
    """TAKE RUN button selected"""
    await callback_query.message.edit_text(
        "🏃 **TAKE RUN SELECTED!**\n\n"
        "Send 1 or 2 on bot PM to take run!"
    )
    await callback_query.answer()


# ==================== MATCH CONTROL ====================

async def swap_command(client, message: Message):
    """Swap batting positions"""
    chat_id = message.chat.id
    
    if chat_id in active_games:
        game = active_games[chat_id]
        game["current_batter"], game["current_non_striker"] = game.get("current_non_striker"), game.get("current_batter")
        await message.reply_text("🔄 **Positions Swapped!**")
    else:
        await message.reply_text("❌ No active game found!")


async def end_match_command(client, message: Message):
    """End current match"""
    chat_id = message.chat.id
    
    if chat_id in active_games:
        game = active_games[chat_id]
        final_score = f"{game['current_runs']}/{game['current_wickets']}"
        
        await message.reply_text(
            f"🏆 **Match Ended!** 🏆\n\n"
            f"📊 **Final Score:** {final_score}\n"
            f"📈 **Balls Faced:** {game['current_balls']}\n\n"
            f"Thanks for playing! 🎉\n\n"
            f"Type /startgame to play again"
        )
        
        # Save match to database
        await db.create_match({
            "chat_id": chat_id,
            "score": final_score,
            "balls": game['current_balls'],
            "players": game.get("players", []),
            "created_at": datetime.now()
        })
        
        # Clear active game
        del active_games[chat_id]
        
        # Clear stored numbers
        if chat_id in bowler_number_store:
            del bowler_number_store[chat_id]
        if chat_id in batter_number_store:
            del batter_number_store[chat_id]
        
        # Cancel timers
        if chat_id in bowling_timers:
            bowling_timers[chat_id].cancel()
        if chat_id in batting_timers:
            batting_timers[chat_id].cancel()
    else:
        await message.reply_text("❌ No active game found!")


async def end_match(client, message, chat_id):
    """End match internally"""
    if chat_id in active_games:
        game = active_games[chat_id]
        final_score = f"{game['current_runs']}/{game['current_wickets']}"
        
        await client.send_message(
            chat_id,
            f"🏆 **Match Ended!** 🏆\n\n"
            f"📊 **Final Score:** {final_score}\n"
            f"📈 **Balls Faced:** {game['current_balls']}\n\n"
            f"Thanks for playing! 🎉"
        )
        
        del active_games[chat_id]
        
        # Clear stored numbers
        if chat_id in bowler_number_store:
            del bowler_number_store[chat_id]
        if chat_id in batter_number_store:
            del batter_number_store[chat_id]


# ==================== DM MESSAGE HANDLER ====================

async def handle_bowling_number(client, user_id, number_text):
    """Handle bowling number received in DM"""
    for chat_id, game in active_games.items():
        if game.get("current_bowler") == user_id and game.get("bowling_status") == "waiting_for_number":
            try:
                number = int(number_text)
                if 1 <= number <= 6:
                    game["bowling_status"] = "completed"
                    # Store bowler's number
                    bowler_number_store[chat_id] = number
                    await client.send_message(
                        chat_id,
                        f"🎯 **Bowler sent {number}**\n\n"
                        f"Now waiting for batsman to play...\n"
                        f"Batsman, send your number (1-6) on bot PM!"
                    )
                    await client.send_message(user_id, f"✅ You sent {number}! Waiting for batsman...")
                    return True
                else:
                    await client.send_message(user_id, "❌ Please send number between 1-6!")
            except ValueError:
                if number_text.upper() == "W":
                    # Wicket on purpose
                    game["bowling_status"] = "completed"
                    bowler_number_store[chat_id] = 0
                    await client.send_message(
                        chat_id,
                        f"🎯 **Bowler chose WICKET!**\n\n"
                        f"Batsman, send your number (1-6) on bot PM!"
                    )
                    return True
                else:
                    await client.send_message(user_id, "❌ Please send number between 1-6 or W!")
    return False


async def handle_batting_number(client, user_id, number_text):
    """Handle batting number received in DM"""
    for chat_id, game in active_games.items():
        if game.get("current_batter") == user_id and game.get("batting_status") == "waiting_for_number":
            try:
                number = int(number_text)
                if 1 <= number <= 6:
                    bowler_num = bowler_number_store.get(chat_id, 0)
                    
                    # Check if OUT
                    if bowler_num == number and bowler_num != 0:
                        # WICKET!
                        game["current_wickets"] = game.get("current_wickets", 0) + 1
                        game["current_balls"] = game.get("current_balls", 0) + 1
                        
                        # Send OUT video
                        if OUT_VIDEO_URL:
                            await client.send_video(chat_id, OUT_VIDEO_URL, caption=f"🎯 **Number matches! Player is out!**")
                        else:
                            await client.send_message(chat_id, f"🎯 **Number matches! {user_id} is out!**")
                        
                        response_time = random.randint(30, 150)
                        await client.send_message(
                            chat_id,
                            f"📊 Score: {game['current_runs']}/{game['current_wickets']}\n"
                            f"⏱️ {response_time}ms"
                        )
                        
                        # Clear stored number
                        bowler_number_store[chat_id] = 0
                        
                        # Check match end
                        if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
                            await end_match(client, None, chat_id)
                        else:
                            # Switch to next batsman
                            await switch_to_next_batsman(client, chat_id)
                        
                        await client.send_message(user_id, f"❌ You're OUT! Bowler's number was {bowler_num}")
                        return True
                    else:
                        # NOT OUT - Add runs
                        runs = number
                        game["current_runs"] = game.get("current_runs", 0) + runs
                        game["current_balls"] = game.get("current_balls", 0) + 1
                        game["ball_sequence"].append(runs)
                        
                        # Send runs video
                        if runs == 6 and SIX_VIDEO_URL:
                            await client.send_video(chat_id, SIX_VIDEO_URL, caption=f"🎯 **SIX!** 🚀")
                        elif runs == 4 and FOUR_VIDEO_URL:
                            await client.send_video(chat_id, FOUR_VIDEO_URL, caption=f"🎯 **FOUR!** 💥")
                        elif BATTING_VIDEO_URL:
                            await client.send_video(chat_id, BATTING_VIDEO_URL, caption=f"🏏 **{runs} RUN{'S' if runs > 1 else ''}!**")
                        else:
                            await client.send_message(chat_id, f"🏏 **{runs} RUN{'S' if runs > 1 else ''}!**")
                        
                        response_time = random.randint(30, 150)
                        await client.send_message(
                            chat_id,
                            f"📊 Score: {game['current_runs']}/{game['current_wickets']}\n"
                            f"📈 Balls: {game['current_balls']}/{(game.get('total_overs', 2) * 6)}\n"
                            f"⏱️ {response_time}ms\n\n"
                            f"Bowler: {bowler_num} | Batter: {number}"
                        )
                        
                        # Clear stored number for next ball
                        bowler_number_store[chat_id] = 0
                        
                        # Check match end
                        if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
                            await end_match(client, None, chat_id)
                        else:
                            # Next ball - roles switch
                            game["bowling_status"] = "waiting_for_number"
                            game["batting_status"] = "waiting_for_number"
                            
                            # Show next batter
                            await client.send_message(chat_id, f"🔄 **Next ball! Bowler, send your number (1-6) on bot PM!**")
                        
                        await client.send_message(user_id, f"✅ You sent {number}! {runs} runs added!")
                        return True
                else:
                    await client.send_message(user_id, "❌ Please send number between 1-6!")
            except ValueError:
                await client.send_message(user_id, "❌ Please send a valid number between 1-6!")
    return False
