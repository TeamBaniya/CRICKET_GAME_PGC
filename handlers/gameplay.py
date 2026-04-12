from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from config import BOWLING_VIDEO_URL, BATTING_VIDEO_URL, OUT_VIDEO_URL, WICKET_VIDEO_URL, SIX_VIDEO_URL, FOUR_VIDEO_URL, BOT_USERNAME
import random
import asyncio
from handlers.game import active_games
from datetime import datetime

# Store bowler number
bowler_number_store = {}


# ==================== BOWLING COMMAND ====================

async def bowling_command(client, message: Message):
    """/bowling command - Deep link to open DM directly"""
    print("🔵 DEBUG: bowling_command CALLED")
    user_id = message.from_user.id
    chat_id = message.chat.id

    if chat_id not in active_games:
        print("🔴 DEBUG: No active game found!")
        await message.reply_text("❌ No active game found!")
        return

    game = active_games[chat_id]

    if game.get("current_bowler") != user_id:
        print(f"🔴 DEBUG: User {user_id} is not the bowler! Current bowler: {game.get('current_bowler')}")
        await message.reply_text("❌ You are not the bowler!")
        return

    print(f"🔵 DEBUG: Bowler confirmed: {user_id}")
    game["bowling_status"] = "waiting_for_number"
    game["bowler_name"] = message.from_user.first_name
    game["bowler_id"] = user_id

    # ✅ Send DM to bowler FIRST (with Group button)
    try:
        # Get current batter name
        current_batter_id = game.get("current_batter")
        current_batter_name = "Unknown"
        for player in game.get("players", []):
            if player.get("user_id") == current_batter_id:
                current_batter_name = player.get("first_name")
                break

        # Get over/balls info
        current_balls = game.get("current_balls", 0)
        overs_done = current_balls // 6
        balls_done = current_balls % 6

        # Create group link button for DM
        group_link = f"https://t.me/c/{str(chat_id).replace('-100', '')}"
        dm_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏀 Group", url=group_link, style=ButtonStyle.PRIMARY)]
        ])

        # Try to send image if available
        try:
            from config import BOWLING_DM_IMAGE_URL
            if BOWLING_DM_IMAGE_URL:
                await client.send_photo(
                    user_id,
                    photo=BOWLING_DM_IMAGE_URL,
                    caption=f"🎯 **Current batter: {current_batter_name}**\n\n"
                            f"📊 **OVER BALLS = {overs_done}.{balls_done}**\n\n"
                            f"Send your bowling number (1-6)!\n\n"
                            f"⏰ You have 50 seconds!",
                    reply_markup=dm_buttons
                )
            else:
                await client.send_message(
                    user_id,
                    f"🎯 **Current batter: {current_batter_name}**\n\n"
                    f"📊 **OVER BALLS = {overs_done}.{balls_done}**\n\n"
                    f"Send your bowling number (1-6)!\n\n"
                    f"⏰ You have 50 seconds!",
                    reply_markup=dm_buttons
                )
        except ImportError:
            await client.send_message(
                user_id,
                f"🎯 **Current batter: {current_batter_name}**\n\n"
                f"📊 **OVER BALLS = {overs_done}.{balls_done}**\n\n"
                f"Send your bowling number (1-6)!\n\n"
                f"⏰ You have 50 seconds!",
                reply_markup=dm_buttons
            )
        print("🔵 DEBUG: DM sent to bowler with Group button")
    except Exception as e:
        print(f"🔴 DEBUG: Cannot send DM! Error: {e}")

    # Send message first in group
    await message.reply_text(
        f"🎯 **Hey {message.from_user.first_name}, now you're bowling!**"
    )

    # Wait 2 seconds
    await asyncio.sleep(2)

    # 🔥 Deep Link Button - Directly opens DM (no callback)
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏏 Bowling",
                url=f"https://t.me/{BOT_USERNAME}?start=bowling_{chat_id}",
                style=ButtonStyle.PRIMARY
            )
        ]
    ])

    # Send bowling video with deep link button
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
    print("🔵 DEBUG: Bowling deep link button sent to group")

    # Start 50 second timer
    await start_bowling_timer(client, chat_id, message.from_user.first_name, user_id)


async def start_bowling_timer(client, chat_id, bowler_name, bowler_id):
    """50 second timer for bowler to send number (hidden)"""
    for remaining in range(50, 0, -1):
        if chat_id not in active_games:
            return
        
        game = active_games[chat_id]
        if game.get("bowling_status") != "waiting_for_number":
            return
        
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


# ==================== BATTING COMMAND ====================

async def batting_command(client, message: Message):
    """/batting command - Deep link to open DM directly for batting"""
    print("🔵 DEBUG: batting_command CALLED")
    user_id = message.from_user.id
    chat_id = message.chat.id

    if chat_id not in active_games:
        print("🔴 DEBUG: No active game found!")
        await message.reply_text("❌ No active game found!")
        return

    game = active_games[chat_id]

    if game.get("current_batter") != user_id:
        print(f"🔴 DEBUG: User {user_id} is not the batter! Current batter: {game.get('current_batter')}")
        await message.reply_text("❌ You are not the batter!")
        return

    print(f"🔵 DEBUG: Batter confirmed: {user_id}")
    game["batting_status"] = "waiting_for_number"
    game["batter_name"] = message.from_user.first_name
    game["batter_id"] = user_id

    # ✅ Send DM to batter FIRST (with Group button)
    try:
        # Get current bowler name
        current_bowler_id = game.get("current_bowler")
        current_bowler_name = "Unknown"
        for player in game.get("players", []):
            if player.get("user_id") == current_bowler_id:
                current_bowler_name = player.get("first_name")
                break

        # Get over/balls info
        current_balls = game.get("current_balls", 0)
        overs_done = current_balls // 6
        balls_done = current_balls % 6

        # Create group link button for DM
        group_link = f"https://t.me/c/{str(chat_id).replace('-100', '')}"
        dm_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏀 Group", url=group_link, style=ButtonStyle.PRIMARY)]
        ])

        # Try to send image if available
        try:
            from config import BATTING_DM_IMAGE_URL
            if BATTING_DM_IMAGE_URL:
                await client.send_photo(
                    user_id,
                    photo=BATTING_DM_IMAGE_URL,
                    caption=f"🏏 **Current bowler: {current_bowler_name}**\n\n"
                            f"📊 **OVER BALLS = {overs_done}.{balls_done}**\n\n"
                            f"Send your batting number (1-6)!\n\n"
                            f"⏰ You have 50 seconds!",
                    reply_markup=dm_buttons
                )
            else:
                await client.send_message(
                    user_id,
                    f"🏏 **Current bowler: {current_bowler_name}**\n\n"
                    f"📊 **OVER BALLS = {overs_done}.{balls_done}**\n\n"
                    f"Send your batting number (1-6)!\n\n"
                    f"⏰ You have 50 seconds!",
                    reply_markup=dm_buttons
                )
        except ImportError:
            await client.send_message(
                user_id,
                f"🏏 **Current bowler: {current_bowler_name}**\n\n"
                f"📊 **OVER BALLS = {overs_done}.{balls_done}**\n\n"
                f"Send your batting number (1-6)!\n\n"
                f"⏰ You have 50 seconds!",
                reply_markup=dm_buttons
            )
        print("🔵 DEBUG: DM sent to batter with Group button")
    except Exception as e:
        print(f"🔴 DEBUG: Cannot send DM! Error: {e}")

    # Send message first in group
    await message.reply_text(
        f"🏏 **Hey {message.from_user.first_name}, now you're batting!**"
    )

    # Wait 2 seconds
    await asyncio.sleep(2)

    # 🔥 Deep Link Button - Directly opens DM (no callback)
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏏 Batting",
                url=f"https://t.me/{BOT_USERNAME}?start=batting_{chat_id}",
                style=ButtonStyle.SUCCESS
            )
        ]
    ])

    # Send batting video with deep link button
    if BATTING_VIDEO_URL:
        await client.send_video(
            chat_id,
            video=BATTING_VIDEO_URL,
            caption=f"👏 **{message.from_user.first_name} click below to send your number!**",
            reply_markup=buttons
        )
    else:
        await client.send_message(
            chat_id,
            f"👏 **{message.from_user.first_name} click below to send your number!**",
            reply_markup=buttons
        )
    print("🔵 DEBUG: Batting deep link button sent to group")

    # Start 50 second timer
    await start_batting_timer(client, chat_id, message.from_user.first_name, user_id)


async def start_batting_timer(client, chat_id, batter_name, batter_id):
    """50 second timer for batter to send number (hidden)"""
    for remaining in range(50, 0, -1):
        if chat_id not in active_games:
            return
        
        game = active_games[chat_id]
        if game.get("batting_status") != "waiting_for_number":
            return
        
        await asyncio.sleep(1)
    
    # Timeout - penalty
    if chat_id in active_games and active_games[chat_id].get("batting_status") == "waiting_for_number":
        await client.send_message(
            chat_id,
            f"⏰ **No message received from @{batter_name}, deducting 6 runs from batsman.**\n\n"
            f"❌ **Seems Batting player is not responding, User Eliminated from the game !!**"
        )
        
        await switch_to_next_batsman(client, chat_id)


# ==================== GROUP BATTING HANDLER (for group numbers) ====================

async def handle_group_batting_number(client, message: Message):
    """Handle batting number sent directly in group (without command)"""
    print("🔵 DEBUG: handle_group_batting_number CALLED")
    user_id = message.from_user.id
    chat_id = message.chat.id
    number = int(message.text.strip())
    print(f"🔵 DEBUG: User {user_id} sent number {number} in chat {chat_id}")
    
    # Add thumb emoji reaction 👍
    try:
        await message.react(emoji="👍")
        print("🔵 DEBUG: Added 👍 reaction")
    except:
        pass
    
    if chat_id not in active_games:
        print("🔴 DEBUG: No active game found!")
        await message.reply_text("❌ No active game found! Use /startgame first.")
        return
    
    game = active_games[chat_id]
    print(f"🔵 DEBUG: Game found")
    
    if game.get("current_batter") != user_id:
        print(f"🔴 DEBUG: User {user_id} is not current batter! Current batter: {game.get('current_batter')}")
        await message.reply_text("❌ You are not the current batsman!")
        return
    
    if game.get("batting_status") != "waiting_for_number":
        print(f"🔴 DEBUG: batting_status is {game.get('batting_status')}, not waiting_for_number")
        await message.reply_text("❌ Already processed! Wait for your turn.")
        return
    
    # Get bowler's number
    bowler_num = bowler_number_store.get(chat_id, 0)
    print(f"🔵 DEBUG: Bowler number: {bowler_num}, Batter number: {number}")
    
    # Check if OUT (numbers match)
    if bowler_num == number and bowler_num != 0:
        print("🔵 DEBUG: OUT! Numbers match")
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
    print(f"🔵 DEBUG: NOT OUT! {runs} runs added. Total: {game['current_runs']}/{game['current_wickets']}")
    
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
