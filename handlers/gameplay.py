from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from config import BOWLING_VIDEO_URL, BATTING_VIDEO_URL, OUT_VIDEO_URL, WICKET_VIDEO_URL, SIX_VIDEO_URL, FOUR_VIDEO_URL, BOT_USERNAME, RESULT_IMAGE_URL
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

    # Send message first in group
    await message.reply_text(
        f"🎯 **Hey {message.from_user.first_name}, now you're bowling!**"
    )

    # Wait 2 seconds
    await asyncio.sleep(2)

    # Deep Link Button - Directly opens DM
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
    """50 second timer - after timeout, go to batting screen"""
    for remaining in range(50, 0, -1):
        if chat_id not in active_games:
            return
        
        game = active_games[chat_id]
        if game.get("bowling_status") != "waiting_for_number":
            return
        
        await asyncio.sleep(1)
    
    # Timeout - eliminate bowler and go to batting
    if chat_id in active_games and active_games[chat_id].get("bowling_status") == "waiting_for_number":
        game = active_games[chat_id]
        
        # Send elimination message
        await client.send_message(
            chat_id,
            f"⏰ **@{bowler_name} didn't send number in 50 seconds! Eliminated from the game!**"
        )
        
        # Remove current bowler from players list
        players = game.get("players", [])
        for i, player in enumerate(players):
            if player.get("user_id") == bowler_id:
                players.pop(i)
                break
        
        game["players"] = players
        
        # Check if any players left
        if len(players) == 0:
            await client.send_message(chat_id, "❌ No players left! Game ended!")
            await end_match(client, None, chat_id)
            return
        
        # ✅ GO TO BATTING SCREEN (not bowling again)
        if len(players) > 0:
            game["current_batter"] = players[0]["user_id"]
            game["current_batter_index"] = 0
            game["batting_status"] = "waiting_for_number"
            game["bowling_status"] = "completed"
            
            batter_name = players[0]["first_name"]
            ratings_text = "ND BAT 66 | MENTAL 66 | PACE 63 | PHYSICAL 66"
            
            await client.send_message(
                chat_id,
                f"🏏 **Now Batter: {batter_name} can send number (1-6)!!**\n\n"
                f"📊 **Ratings:** {ratings_text}\n\n"
                f"Type your number (1-6) in this group!"
            )
            
            # Send batting video
            if BATTING_VIDEO_URL:
                await client.send_video(chat_id, BATTING_VIDEO_URL)
            
            # Start batting timer
            await start_batting_timer(client, chat_id, batter_name, players[0]["user_id"])


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


# ==================== BOWLING BUTTON CALLBACK (DM Handler) ====================

async def bowling_button_callback(callback_query):
    """Handle bowling button click - send DM to bowler"""
    print("🔵 DEBUG: bowling_button_callback CALLED")
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
    
    # Send DM to bowler
    try:
        await callback_query._client.send_message(
            user_id,
            f"🎯 **Current batter: {current_batter_name}**\n\n"
            f"Send your bowling number (1-6)!\n\n"
            f"⏰ You have 50 seconds!\n\n"
            f"Just type a number between 1-6 and send."
        )
        print(f"🔵 DEBUG: DM sent to {user_id}")
    except Exception as e:
        print(f"🔴 DEBUG: Cannot send DM! Error: {e}")
        await callback_query.message.reply_text(f"❌ Cannot send DM! Error: {e}")


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

    await message.reply_text(
        f"🏏 **Hey {message.from_user.first_name}, now you're batting!**"
    )

    await asyncio.sleep(2)

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏏 Batting",
                url=f"https://t.me/{BOT_USERNAME}?start=batting_{chat_id}",
                style=ButtonStyle.SUCCESS
            )
        ]
    ])

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

    await start_batting_timer(client, chat_id, message.from_user.first_name, user_id)


async def start_batting_timer(client, chat_id, batter_name, batter_id):
    """50 second timer - if no number, eliminate batter and move to next"""
    for remaining in range(50, 0, -1):
        if chat_id not in active_games:
            return
        
        game = active_games[chat_id]
        if game.get("batting_status") != "waiting_for_number":
            return
        
        await asyncio.sleep(1)
    
    if chat_id in active_games and active_games[chat_id].get("batting_status") == "waiting_for_number":
        game = active_games[chat_id]
        
        await client.send_message(
            chat_id,
            f"⏰ **@{batter_name} didn't send number in 50 seconds! Eliminated from the game!**"
        )
        
        players = game.get("players", [])
        for i, player in enumerate(players):
            if player.get("user_id") == batter_id:
                players.pop(i)
                break
        
        game["players"] = players
        
        if len(players) == 0:
            await client.send_message(chat_id, "❌ No players left! Game ended!")
            await end_match(client, None, chat_id)
            return
        
        if len(players) > 0:
            game["current_batter"] = players[0]["user_id"]
            game["current_batter_index"] = 0
            game["batting_status"] = "waiting_for_number"
            
            await client.send_message(
                chat_id,
                f"🔄 **Hey {players[0]['first_name']}, now you're batting!**\n\n"
                f"Send your number (1-6) in group to play!"
            )


# ==================== GROUP BATTING HANDLER (for group numbers) ====================

async def handle_group_batting_number(client, message: Message):
    """Handle batting number sent directly in group (without command)"""
    print("🔵 DEBUG: handle_group_batting_number CALLED")
    user_id = message.from_user.id
    chat_id = message.chat.id
    number = int(message.text.strip())
    print(f"🔵 DEBUG: User {user_id} sent number {number} in chat {chat_id}")
    
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
    
    bowler_num = bowler_number_store.get(chat_id, 0)
    print(f"🔵 DEBUG: Bowler number: {bowler_num}, Batter number: {number}")
    
    # Check if OUT (numbers match)
    if bowler_num == number and bowler_num != 0:
        print("🔵 DEBUG: OUT! Numbers match")
        game["current_wickets"] = game.get("current_wickets", 0) + 1
        game["current_balls"] = game.get("current_balls", 0) + 1
        game["batting_status"] = "completed"
        
        for player in game.get("players", []):
            if player.get("user_id") == user_id:
                player["runs"] = game.get("current_runs", 0)
                player["balls"] = game.get("current_balls", 0)
                player["fours"] = game.get("fours", 0)
                player["sixes"] = game.get("sixes", 0)
                player["ball_sequence"] = game.get("ball_sequence", [])
                break
        
        if WICKET_VIDEO_URL:
            await client.send_video(chat_id, WICKET_VIDEO_URL, caption=f"🎯 **WICKET!** 🎯")
        
        if OUT_VIDEO_URL:
            await client.send_video(chat_id, OUT_VIDEO_URL)
        
        username = message.from_user.username
        if username:
            await client.send_message(chat_id, f"**Number matches, @{username} is out!**")
        else:
            await client.send_message(chat_id, f"**Number matches, {message.from_user.first_name} is out!**")
        
        response_time = random.randint(30, 150)
        await message.reply_text(
            f"📊 Score: {game['current_runs']}/{game['current_wickets']}\n"
            f"⏱️ {response_time}ms\n\n"
            f"Bowler: {bowler_num} | Batter: {number}"
        )
        
        bowler_number_store[chat_id] = 0
        
        if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
            await end_match(client, message, chat_id)
            return
        
        await switch_to_next_batsman(client, chat_id)
        return
    
    # NOT OUT - Add runs
    runs = number
    game["current_runs"] = game.get("current_runs", 0) + runs
    game["current_balls"] = game.get("current_balls", 0) + 1
    game["ball_sequence"].append(runs)
    game["batting_status"] = "completed"
    
    if runs == 4:
        game["fours"] = game.get("fours", 0) + 1
    elif runs == 6:
        game["sixes"] = game.get("sixes", 0) + 1
    
    print(f"🔵 DEBUG: NOT OUT! {runs} runs added. Total: {game['current_runs']}/{game['current_wickets']}")
    
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
    
    bowler_number_store[chat_id] = 0
    
    if game['current_balls'] >= (game.get('total_overs', 2) * 6) or game['current_wickets'] >= 10:
        await end_match(client, message, chat_id)
        return
    
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
    """End match internally with result image and clickable players"""
    if chat_id in active_games:
        game = active_games[chat_id]
        current_runs = game.get("current_runs", 0)
        current_wickets = game.get("current_wickets", 0)
        current_balls = game.get("current_balls", 0)
        final_score = f"{current_runs}/{current_wickets}"
        
        # Update final player stats
        for player in game.get("players", []):
            if player.get("user_id") == game.get("current_batter"):
                player["runs"] = current_runs
                player["balls"] = current_balls
                player["fours"] = game.get("fours", 0)
                player["sixes"] = game.get("sixes", 0)
                player["ball_sequence"] = game.get("ball_sequence", [])
                break
        
        # Prepare players list for result with clickable names
        players = game.get("players", [])
        players_list = ""
        
        icons = ["🟢", "⚽", "🔥", "🌞", "💬", "🎮", "🏀", "🐍", "🕊️", "⭐", "⚡", "💎"]
        
        for i, player in enumerate(players):
            icon = icons[i % len(icons)]
            name = player.get('first_name', 'Unknown')
            username = player.get('username')
            runs = player.get('runs', 0)
            balls = player.get('balls', 0)
            fours = player.get('fours', 0)
            sixes = player.get('sixes', 0)
            user_id = player.get('user_id')
            ball_seq = player.get('ball_sequence', [])
            
            seq_str = ", ".join(str(s) for s in ball_seq[-8:]) if ball_seq else "-"
            
            if username:
                clickable_name = f"@{username}"
            else:
                clickable_name = f'<a href="tg://user?id={user_id}">{name}</a>'
            
            players_list += f"{i+1}. {icon} **{clickable_name}** = {runs}({balls})\n"
            players_list += f"    ╰⊚ 4️⃣s: {fours:02d}, 6️⃣s: {sixes:02d} - ID: `{user_id}`\n"
            players_list += f"      ╰⊚ ({seq_str})\n\n"
        
        # First: Send "Game Ended" message
        await client.send_message(
            chat_id,
            f"🏏 **Game Ended**\n\n"
            f"📊 Final Score: {final_score}\n"
            f"📈 Balls: {current_balls}\n\n"
            f"Result loading... 🎯"
        )
        
        # Second: Send result image with players list
        result_caption = f"─────⊱ 𝐒𝐨𝐥𝐨 𝐏𝐥𝐚𝐲𝐞𝐫𝐬 ⊰────\n\n{players_list}\n\n🎮 **Play Again:** /startgame"
        
        if RESULT_IMAGE_URL:
            await client.send_photo(
                chat_id,
                photo=RESULT_IMAGE_URL,
                caption=result_caption,
                parse_mode="HTML"
            )
        else:
            await client.send_message(
                chat_id, 
                result_caption,
                parse_mode="HTML"
            )
        
        await db.create_match({
            "chat_id": chat_id,
            "score": final_score,
            "balls": current_balls,
            "players": players,
            "created_at": datetime.now()
        })
        
        del active_games[chat_id]
        
        if chat_id in bowler_number_store:
            del bowler_number_store[chat_id]
