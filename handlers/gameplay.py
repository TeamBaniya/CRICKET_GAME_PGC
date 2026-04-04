# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from config import BOWLING_SPEEDS_BUTTONS, BATTING_RATINGS
import random
import asyncio
from datetime import datetime

# Store active game sessions
active_games = {}
bowling_timers = {}
batting_timers = {}

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
        await message.reply_text(
            "❌ **Usage:** /bowling <speed>\n\n"
            f"**Available speeds:**\n{', '.join(BOWLING_SPEEDS_BUTTONS)}\n\n"
            "Example: /bowling FAST"
        )
        return
    
    speed = args[1].upper()
    if speed not in BOWLING_SPEEDS_BUTTONS:
        await message.reply_text(
            f"❌ Invalid speed! Choose from:\n{', '.join(BOWLING_SPEEDS_BUTTONS)}"
        )
        return
    
    # Cancel timer if exists
    if chat_id in bowling_timers:
        bowling_timers[chat_id].cancel()
    
    # Save bowling selection
    game["selected_speed"] = speed
    game["bowling_status"] = "waiting_for_number"
    
    await message.reply_text(
        f"✅ **Speed {speed} selected!**\n\n"
        f"Now send number on bot PM (1-6 or W for wicket)\n"
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
    
    # Show bowling speed options
    await show_bowling_speed_options_to_user(client, chat_id, next_bowler["user_id"])


async def show_bowling_speed_options_to_user(client, chat_id, bowler_id):
    """Send bowling speed options to bowler in DM"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(speed, callback_data=speed.lower(), style=ButtonStyle.PRIMARY)
            for speed in BOWLING_SPEEDS_BUTTONS[i:i+3]
        ]
        for i in range(0, len(BOWLING_SPEEDS_BUTTONS), 3)
    ])
    
    try:
        await client.send_message(
            bowler_id,
            "🎯 **Choose your bowling speed:**",
            reply_markup=buttons
        )
    except Exception:
        pass


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
        f"Now send number on bot PM (1-6 or W for wicket)\n"
        f"⏰ You have 60 seconds!"
    )
    await callback_query.answer()
    
    # Start timer
    await start_bowling_timer(callback_query._client, chat_id, callback_query.from_user.first_name)


async def show_bowling_speed_options(callback_query):
    """Show bowling speed options in group"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(speed, callback_data=speed.lower(), style=ButtonStyle.PRIMARY)
            for speed in BOWLING_SPEEDS_BUTTONS[i:i+3]
        ]
        for i in range(0, len(BOWLING_SPEEDS_BUTTONS), 3)
    ])
    
    await callback_query.message.edit_text(
        "🎯 **Choose your bowling speed:**",
        reply_markup=buttons
    )
    await callback_query.answer()


# ==================== BATTING COMMANDS ====================

async def batting_command(client, message: Message):
    """/batting command - Select batsman"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    args = message.text.split()
    
    if chat_id not in active_games:
        await message.reply_text("❌ No active game found! Use /startgame first.")
        return
    
    game = active_games[chat_id]
    
    if len(args) < 2:
        await message.reply_text(
            "❌ **Usage:** /batting <number>\n\n"
            "Send number (1-6) to play the ball!\n"
            "Example: /batting 4"
        )
        return
    
    try:
        number = int(args[1])
        if number not in range(1, 7):
            raise ValueError
    except ValueError:
        await message.reply_text("❌ Please send a number between 1-6!")
        return
    
    # Calculate runs based on number
    runs = calculate_runs(number, game.get("selected_speed", "FAST"))
    
    # Update game score
    game["current_runs"] = game.get("current_runs", 0) + runs
    game["current_balls"] = game.get("current_balls", 0) + 1
    game["ball_sequence"].append(runs)
    
    # Prepare result message
    if runs == 6:
        result_text = "🎯 **SIX!** 🚀"
        video_url = None  # Add your SIX video link here
    elif runs == 4:
        result_text = "🎯 **FOUR!** 💥"
        video_url = None  # Add your FOUR video link here
    elif runs == 0:
        result_text = "⚪ **DOT BALL!**"
        video_url = None
    else:
        result_text = f"🏏 **{runs} RUN{'S' if runs > 1 else ''}!**"
        video_url = None
    
    response_time = random.randint(30, 150)
    
    await message.reply_text(
        f"{result_text}\n\n"
        f"⏱️ {response_time}ms\n\n"
        f"📊 Score: {game['current_runs']}/{game['current_wickets']}\n"
        f"📈 Balls: {game['current_balls']}/{(game.get('total_overs', 2) * 6)}"
    )
    
    # Check for match end
    if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
        await end_match(client, message, chat_id)
        return
    
    # Switch roles - now bowler becomes batter
    game["current_bowler"], game["current_batter"] = game.get("current_batter"), game.get("current_bowler")
    game["batting_status"] = "waiting_for_number"
    
    # Show batting ratings to batter
    await show_batting_ratings_to_user(client, chat_id, game["current_batter"])


async def show_batting_ratings_to_user(client, chat_id, batter_id):
    """Send batting ratings to batter in DM"""
    ratings_text = " | ".join([f"{k} {v}" for k, v in BATTING_RATINGS.items()])
    
    try:
        await client.send_message(
            batter_id,
            f"🏏 **Now Batter can send number (1-6)!!**\n\n"
            f"📊 **Ratings:** {ratings_text}\n\n"
            f"Send a number between 1-6 to play the ball!"
        )
    except Exception:
        pass


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


def calculate_runs(number: int, speed: str) -> int:
    """Calculate runs based on number and bowling speed"""
    # Simple logic - can be made more complex
    if number == 6:
        return 6
    elif number == 5:
        return 4
    elif number == 4:
        return 4
    elif number == 3:
        return 3
    elif number == 2:
        return 2
    elif number == 1:
        return 1
    return 0


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


# ==================== DM MESSAGE HANDLER ====================

async def handle_bowling_number(client, user_id, number_text):
    """Handle bowling number received in DM"""
    # Find which game this user is in
    for chat_id, game in active_games.items():
        if game.get("current_bowler") == user_id and game.get("bowling_status") == "waiting_for_number":
            # Process the number
            is_wicket = number_text.upper() == "W"
            
            if is_wicket:
                game["current_wickets"] = game.get("current_wickets", 0) + 1
                await client.send_message(
                    chat_id,
                    f"🎯 **WICKET!** 🎯\n\n"
                    f"⏱️ {random.randint(30, 150)}ms\n\n"
                    f"📊 Score: {game['current_runs']}/{game['current_wickets']}"
                )
                await switch_to_next_bowler(client, chat_id)
            else:
                try:
                    runs = int(number_text)
                    if 1 <= runs <= 6:
                        game["bowling_status"] = "completed"
                        # Store the number for batting
                        game["bowled_number"] = runs
                        await client.send_message(
                            chat_id,
                            f"🎯 **Bowler sent {runs}**\n\n"
                            f"Now waiting for batsman to play..."
                        )
                    else:
                        await client.send_message(user_id, "❌ Please send number between 1-6 or W!")
                except ValueError:
                    await client.send_message(user_id, "❌ Please send number between 1-6 or W!")
            return True
    
    return False
