from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from config import BOWLING_VIDEO_URL, BATTING_VIDEO_URL, OUT_VIDEO_URL, WICKET_VIDEO_URL, SIX_VIDEO_URL, FOUR_VIDEO_URL
import random
import asyncio
from handlers.game import active_games
from datetime import datetime

# Store bowler number
bowler_number_store = {}


# ==================== BOWLING COMMAND ====================

async def bowling_command(client, message: Message):
    """/bowling command - Simple callback button"""
    user_id = message.from_user.id
    chat_id = message.chat.id

    if chat_id not in active_games:
        await message.reply_text("❌ No active game found!")
        return

    game = active_games[chat_id]

    if game.get("current_bowler") != user_id:
        await message.reply_text("❌ You are not the bowler!")
        return

    game["bowling_status"] = "waiting_for_number"
    game["bowler_name"] = message.from_user.first_name
    game["bowler_id"] = user_id

    # Send message first
    await message.reply_text(
        f"🎯 **Hey {message.from_user.first_name}, now you're bowling!**"
    )

    # Wait 2 seconds
    await asyncio.sleep(2)

    # Simple callback button
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 Bowling", callback_data="bowling_btn", style=ButtonStyle.PRIMARY)]
    ])

    # Send bowling video with button
    if BOWLING_VIDEO_URL:
        await client.send_video(
            chat_id,
            video=BOWLING_VIDEO_URL,
            caption=f"👏 **{message.from_user.first_name} click below to send your number!**",
            reply_markup=buttons
        )
    else:
        await client.send_message(
            chat_id,
            f"👏 **{message.from_user.first_name} click below to send your number!**",
            reply_markup=buttons
        )

    # Start 60 second timer
    await start_bowling_timer(client, chat_id, message.from_user.first_name, user_id)


async def start_bowling_timer(client, chat_id, bowler_name, bowler_id):
    """60 second timer for bowler to send number with mentions"""
    for remaining in range(60, 0, -1):
        if chat_id not in active_games:
            return
        
        game = active_games[chat_id]
        if game.get("bowling_status") != "waiting_for_number":
            return
        
        if remaining == 30:
            await client.send_message(
                chat_id,
                f"⚠️ **@{bowler_name} you have 30 seconds left! Please send your number quickly!**"
            )
        elif remaining == 10:
            await client.send_message(
                chat_id,
                f"⏰ **@{bowler_name} Last 10 seconds! Send your number NOW!**"
            )
        
        await asyncio.sleep(1)
    
    # Timeout - penalty
    if chat_id in active_games and active_games[chat_id].get("bowling_status") == "waiting_for_number":
        await client.send_message(
            chat_id,
            f"⏰ **No message received from @{bowler_name}, deducting 6 runs of bowler.**\n\n"
            f"❌ **Seems Bowling player is not responding, User Eliminated from the game !!**"
        )
        
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
    game["bowling_status"] = "waiting_for_number"
    game["bowler_name"] = next_bowler["first_name"]
    game["bowler_id"] = next_bowler["user_id"]
    
    await client.send_message(
        chat_id,
        f"🔄 **Hey {next_bowler['first_name']}, now you're bowling!**"
    )


# ==================== BOWLING BUTTON CALLBACK ====================

async def bowling_button_callback(callback_query):
    """Handle bowling button click - send DM to bowler with batter name"""
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    if chat_id not in active_games:
        await callback_query.answer("No active game!", show_alert=True)
        return
    
    game = active_games[chat_id]
    if game.get("current_bowler") != user_id:
        await callback_query.answer("You are not the current bowler!", show_alert=True)
        return
    
    if game.get("bowling_status") != "waiting_for_number":
        await callback_query.answer("Already processed!", show_alert=True)
        return
    
    # Get current batter name
    current_batter_id = game.get("current_batter")
    current_batter_name = "Unknown"
    for player in game.get("players", []):
        if player.get("user_id") == current_batter_id:
            current_batter_name = player.get("first_name")
            break
    
    await callback_query.answer("Check your DM!")
    
    # Update group message
    await callback_query.message.edit_text(f"✅ **{callback_query.from_user.first_name} check your DM!**")
    
    # Send DM to bowler with batter name
    try:
        await callback_query._client.send_message(
            user_id,
            f"🎯 **Current batter: {current_batter_name}**\n\n"
            f"Send your bowling number (1-6)!\n\n"
            f"⏰ You have 60 seconds!\n\n"
            f"Just type a number between 1-6 and send."
        )
        print(f"🔵 DEBUG: DM sent to {user_id}")
    except Exception as e:
        print(f"🔴 DEBUG: Cannot send DM! Error: {e}")
        await callback_query.message.reply_text(f"❌ Cannot send DM! Error: {e}")


# ==================== GROUP BATTING HANDLER ====================

async def handle_group_batting_number(client, message: Message):
    """Handle batting number sent directly in group (without command)"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    number = int(message.text.strip())
    
    # Add thumb emoji reaction 👍
    try:
        await message.react(emoji="👍")
    except:
        pass
    
    if chat_id not in active_games:
        await message.reply_text("❌ No active game found! Use /startgame first.")
        return
    
    game = active_games[chat_id]
    if game.get("current_batter") != user_id:
        await message.reply_text("❌ You are not the current batsman!")
        return
    
    if game.get("batting_status") != "waiting_for_number":
        await message.reply_text("❌ Already processed! Wait for your turn.")
        return
    
    # Get bowler's number
    bowler_num = bowler_number_store.get(chat_id, 0)
    
    # Check if OUT (numbers match)
    if bowler_num == number and bowler_num != 0:
        # WICKET!
        game["current_wickets"] = game.get("current_wickets", 0) + 1
        game["current_balls"] = game.get("current_balls", 0) + 1
        game["batting_status"] = "completed"
        
        # Send WICKET video first
        if WICKET_VIDEO_URL:
            await client.send_video(chat_id, WICKET_VIDEO_URL, caption=f"🎯 **WICKET!** 🎯")
        
        # Send OUT video
        if OUT_VIDEO_URL:
            await client.send_video(chat_id, OUT_VIDEO_URL, caption=f"❌ **Number matches! {message.from_user.first_name} is out!**")
        else:
            await message.reply_text(f"❌ **Number matches! {message.from_user.first_name} is out!**")
        
        response_time = random.randint(30, 150)
        await message.reply_text(
            f"📊 Score: {game['current_runs']}/{game['current_wickets']}\n"
            f"⏱️ {response_time}ms\n\n"
            f"Bowler: {bowler_num} | Batter: {number}\n"
            f"❌ **OUT!**"
        )
        
        # Clear stored number
        bowler_number_store[chat_id] = 0
        
        # Check for match end
        if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
            await end_match(client, message, chat_id)
            return
        
        # Switch to next batsman
        await switch_to_next_batsman(client, chat_id)
        return
    
    # NOT OUT - Add runs (runs = batter's number)
    runs = number
    game["current_runs"] = game.get("current_runs", 0) + runs
    game["current_balls"] = game.get("current_balls", 0) + 1
    game["ball_sequence"].append(runs)
    game["batting_status"] = "completed"
    
    # Send runs video based on runs
    if runs == 6 and SIX_VIDEO_URL:
        await client.send_video(chat_id, SIX_VIDEO_URL, caption=f"🎯 **SIX!** 🚀")
    elif runs == 5:
        await message.reply_text(f"🏏 **{runs} RUNS!**")
    elif runs == 4 and FOUR_VIDEO_URL:
        await client.send_video(chat_id, FOUR_VIDEO_URL, caption=f"🎯 **FOUR!** 💥")
    elif runs == 3:
        await message.reply_text(f"🏏 **{runs} RUNS!**")
    elif runs == 2:
        await message.reply_text(f"🏏 **{runs} RUNS!**")
    elif runs == 1:
        await message.reply_text(f"🏏 **{runs} RUN!**")
    elif BATTING_VIDEO_URL:
        await client.send_video(chat_id, BATTING_VIDEO_URL, caption=f"🏏 **{runs} RUN{'S' if runs > 1 else ''}!**")
    else:
        await message.reply_text(f"🏏 **{runs} RUN{'S' if runs > 1 else ''}!**")
    
    response_time = random.randint(30, 150)
    await message.reply_text(
        f"📊 Score: {game['current_runs']}/{game['current_wickets']}\n"
        f"📈 Balls: {game['current_balls']}/{(game.get('total_overs', 2) * 6)}\n"
        f"⏱️ {response_time}ms\n\n"
        f"Bowler: {bowler_num} | Batter: {number}\n"
        f"🏏 **{runs} RUNS!**"
    )
    
    # Clear stored number for next ball
    bowler_number_store[chat_id] = 0
    
    # Check for match end
    if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
        await end_match(client, message, chat_id)
        return
    
    # Next ball - ask bowler
    game["bowling_status"] = "waiting_for_number"
    game["batting_status"] = "waiting_for_number"
    
    await client.send_message(
        chat_id,
        f"🔄 **Next ball! Bowler, click the BOWLING button!**"
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
            f"🔄 **Hey {next_batter['first_name']}, now you're batting!**\n\n"
            f"Send your number (1-6) in group to play!"
        )
    else:
        await end_match(client, None, chat_id)


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
        current_runs = game.get("current_runs", 0)
        current_wickets = game.get("current_wickets", 0)
        current_balls = game.get("current_balls", 0)
        final_score = f"{current_runs}/{current_wickets}"
        
        await message.reply_text(
            f"🏆 **Match Ended!** 🏆\n\n"
            f"📊 **Final Score:** {final_score}\n"
            f"📈 **Balls Faced:** {current_balls}\n\n"
            f"Thanks for playing! 🎉\n\n"
            f"Type /startgame to play again"
        )
        
        await db.create_match({
            "chat_id": chat_id,
            "score": final_score,
            "balls": current_balls,
            "players": game.get("players", []),
            "created_at": datetime.now()
        })
        
        del active_games[chat_id]
        
        if chat_id in bowler_number_store:
            del bowler_number_store[chat_id]
    else:
        await message.reply_text("❌ No active game found!")


async def end_match(client, message, chat_id):
    """End match internally"""
    if chat_id in active_games:
        game = active_games[chat_id]
        current_runs = game.get("current_runs", 0)
        current_wickets = game.get("current_wickets", 0)
        current_balls = game.get("current_balls", 0)
        final_score = f"{current_runs}/{current_wickets}"
        
        await client.send_message(
            chat_id,
            f"🏆 **Match Ended!** 🏆\n\n"
            f"📊 **Final Score:** {final_score}\n"
            f"📈 **Balls Faced:** {current_balls}\n\n"
            f"Thanks for playing! 🎉"
        )
        
        del active_games[chat_id]
        
        if chat_id in bowler_number_store:
            del bowler_number_store[chat_id]
