# TODO: Add your code here
from pyrogram.types import Message
from handlers.solo import solo_play_number, solo_wicket
from database import db
import random

# Store bowler and batter numbers
bowler_number_store = {}
batter_number_store = {}


async def handle_dm_message(client, message: Message):
    """Handle messages received in bot's DM"""
    user_id = message.from_user.id
    text = message.text.upper().strip()
    
    # ========== SOLO MODE HANDLING ==========
    from handlers.solo import solo_games
    if user_id in solo_games:
        game = solo_games[user_id]
        if game.get("status") == "batting":
            
            if text == "W":
                # Wicket
                result = await solo_wicket(user_id)
                if result:
                    if result.get("is_match_over"):
                        await message.reply_text(
                            f"🎯 **WICKET!** 🎯\n\n"
                            f"📊 **Final Score:** {result['current_score']}\n"
                            f"🏆 **Match Over!**\n\n"
                            f"Type /solo_start to play again!"
                        )
                    else:
                        await message.reply_text(
                            f"🎯 **WICKET!** 🎯\n\n"
                            f"📊 **Score:** {result['current_score']}\n"
                            f"📈 **Balls Left:** {result['balls_left']}\n\n"
                            f"Continue playing! Send next number (1-6)"
                        )
                return
            
            elif text.isdigit() and 1 <= int(text) <= 6:
                # Valid number
                number = int(text)
                result = await solo_play_number(user_id, number)
                
                if result:
                    if result.get("is_match_over"):
                        await message.reply_text(
                            f"🏏 **{result['runs']} RUNS!**\n\n"
                            f"🎉 **Match Completed!** 🎉\n"
                            f"📊 **Final Score:** {result['current_score']}\n"
                            f"🔴 4s: {result['fours']} | 🟢 6s: {result['sixes']}\n\n"
                            f"Type /solo_start to play again!"
                        )
                    else:
                        await message.reply_text(
                            f"🏏 **{result['runs']} RUNS!**\n\n"
                            f"📊 **Score:** {result['current_score']}\n"
                            f"📈 **Balls Left:** {result['balls_left']}\n"
                            f"🔴 4s: {result['fours']} | 🟢 6s: {result['sixes']}\n\n"
                            f"Send next number (1-6)"
                        )
                return
            else:
                await message.reply_text(
                    "❌ **Invalid input!**\n\n"
                    "Send a number between **1-6** to play,\n"
                    "or send **W** for wicket!"
                )
                return
    
    # ========== TEAM MODE - BOWLING HANDLING ==========
    from handlers.gameplay import active_games
    from config import OUT_VIDEO_URL, SIX_VIDEO_URL, FOUR_VIDEO_URL, BATTING_VIDEO_URL
    
    # Check for bowling (bowler sending number)
    for chat_id, game in active_games.items():
        if game.get("current_bowler") == user_id and game.get("bowling_status") == "waiting_for_number":
            if text == "W":
                # Bowler chose Wicket
                game["bowling_status"] = "completed"
                bowler_number_store[chat_id] = 0
                await client.send_message(
                    chat_id,
                    f"🎯 **Bowler chose WICKET!**\n\n"
                    f"Now waiting for batsman to play...\n"
                    f"Batsman, send your number (1-6) on bot PM!"
                )
                await message.reply_text("✅ You chose WICKET! Waiting for batsman...")
                return
                
            elif text.isdigit() and 1 <= int(text) <= 6:
                # Bowler sent valid number
                number = int(text)
                game["bowling_status"] = "completed"
                bowler_number_store[chat_id] = number
                await client.send_message(
                    chat_id,
                    f"🎯 **Bowler sent {number}**\n\n"
                    f"Now waiting for batsman to play...\n"
                    f"Batsman, send your number (1-6) on bot PM!"
                )
                await message.reply_text(f"✅ You sent {number}! Waiting for batsman...")
                return
            else:
                await message.reply_text(
                    "❌ **Invalid input!**\n\n"
                    "Send a number between **1-6** or **W** for wicket!"
                )
                return
    
    # ========== TEAM MODE - BATTING HANDLING ==========
    for chat_id, game in active_games.items():
        if game.get("current_batter") == user_id and game.get("batting_status") == "waiting_for_number":
            if text.isdigit() and 1 <= int(text) <= 6:
                number = int(text)
                bowler_num = bowler_number_store.get(chat_id, 0)
                
                # CHECK IF OUT (Numbers match)
                if bowler_num == number and bowler_num != 0:
                    # WICKET!
                    game["current_wickets"] = game.get("current_wickets", 0) + 1
                    game["current_balls"] = game.get("current_balls", 0) + 1
                    game["batting_status"] = "completed"
                    
                    # Send OUT video
                    if OUT_VIDEO_URL:
                        await client.send_video(chat_id, OUT_VIDEO_URL, caption=f"🎯 **Number matches! {message.from_user.first_name} is out!**")
                    else:
                        await client.send_message(chat_id, f"🎯 **Number matches! {message.from_user.first_name} is out!**")
                    
                    response_time = random.randint(30, 150)
                    await client.send_message(
                        chat_id,
                        f"📊 Score: {game['current_runs']}/{game['current_wickets']}\n"
                        f"📈 Balls: {game['current_balls']}/{(game.get('total_overs', 2) * 6)}\n"
                        f"⏱️ {response_time}ms\n\n"
                        f"❌ Bowler: {bowler_num} | Batter: {number}\n"
                        f"**OUT!**"
                    )
                    
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
                    
                else:
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
                        f"Bowler: {bowler_num} | Batter: {number}\n"
                        f"🏏 **{runs} RUNS!**"
                    )
                    
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
                        
                        # Switch roles - bowler becomes batter for next ball? No, new bowler
                        # Find next bowler
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
                    return
            else:
                await message.reply_text(
                    "❌ **Invalid input!**\n\n"
                    "Send a number between **1-6** to play the ball!"
                )
                return
    
    # Default response - no active game
    await message.reply_text(
        "🎮 **Cricket Game Bot**\n\n"
        "You are not in an active game session.\n\n"
        "Start a game with:\n"
        "• /solo_start - Play solo\n"
        "• /startgame - Create team match\n"
        "• /joingame - Join existing game"
    )


async def end_match_team(client, chat_id, game):
    """End team match"""
    final_score = f"{game['current_runs']}/{game['current_wickets']}"
    
    await client.send_message(
        chat_id,
        f"🏆 **Match Ended!** 🏆\n\n"
        f"📊 **Final Score:** {final_score}\n"
        f"📈 **Balls Faced:** {game['current_balls']}\n\n"
        f"Thanks for playing! 🎉\n\n"
        f"Type /startgame to play again"
    )
    
    # Save to database
    from database import db
    await db.create_match({
        "chat_id": chat_id,
        "score": final_score,
        "balls": game['current_balls'],
        "players": game.get("players", []),
        "created_at": datetime.now()
    })
    
    # Clear game
    from handlers.gameplay import active_games
    if chat_id in active_games:
        del active_games[chat_id]
    
    # Clear stored numbers
    if chat_id in bowler_number_store:
        del bowler_number_store[chat_id]


async def switch_to_next_batsman_team(client, chat_id, game):
    """Switch to next batsman after wicket"""
    players = game.get("players", [])
    current_batter_index = game.get("current_batter_index", 0)
    next_index = current_batter_index + 1
    
    if next_index < len(players):
        next_batter = players[next_index]
        game["current_batter"] = next_batter["user_id"]
        game["current_batter_index"] = next_index
        game["batting_status"] = "waiting_for_number"
        game["bowling_status"] = "waiting_for_number"
        
        await client.send_message(
            chat_id,
            f"🔄 **New batsman! Hey {next_batter['first_name']}, send your number (1-6) on bot PM!**"
        )
    else:
        # No more batsmen - match over
        await end_match_team(client, chat_id, game)


# Import datetime for timestamp
from datetime import datetime
