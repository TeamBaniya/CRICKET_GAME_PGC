# TODO: Add your code here
from pyrogram.types import Message
from handlers.solo import solo_play_number, solo_wicket
from handlers.gameplay import handle_bowling_number
from database import db
import random

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
    
    # ========== BOWLING MODE HANDLING ==========
    from handlers.gameplay import active_games
    for chat_id, game in active_games.items():
        if game.get("current_bowler") == user_id and game.get("bowling_status") == "waiting_for_number":
            if text == "W":
                # Wicket
                await client.send_message(
                    chat_id,
                    f"🎯 **WICKET!** 🎯\n\n"
                    f"⏱️ {random.randint(30, 150)}ms\n\n"
                    f"Great bowling!"
                )
                await message.reply_text("✅ Wicket sent to the game!")
                return
            elif text.isdigit() and 1 <= int(text) <= 6:
                # Valid number
                game["bowled_number"] = int(text)
                game["bowling_status"] = "completed"
                await client.send_message(
                    chat_id,
                    f"🎯 **Bowler sent {text}**\n\n"
                    f"⏱️ {random.randint(30, 150)}ms\n\n"
                    f"Now waiting for batsman..."
                )
                await message.reply_text(f"✅ Number {text} sent to the game!")
                return
            else:
                await message.reply_text(
                    "❌ **Invalid input!**\n\n"
                    "Send a number between **1-6** or **W** for wicket!"
                )
                return
    
    # ========== BATTING MODE HANDLING ==========
    for chat_id, game in active_games.items():
        if game.get("current_batter") == user_id and game.get("batting_status") == "waiting_for_number":
            if text.isdigit() and 1 <= int(text) <= 6:
                number = int(text)
                # Calculate runs based on bowler's number
                bowler_number = game.get("bowled_number", random.randint(1, 6))
                runs = (number + bowler_number) % 7
                if runs == 0:
                    runs = 1
                
                game["current_runs"] = game.get("current_runs", 0) + runs
                game["batting_status"] = "completed"
                
                if runs == 6:
                    result_text = "🎯 **SIX!** 🚀"
                elif runs == 4:
                    result_text = "🎯 **FOUR!** 💥"
                else:
                    result_text = f"🏏 **{runs} RUN{'S' if runs > 1 else ''}!**"
                
                await client.send_message(
                    chat_id,
                    f"{result_text}\n\n"
                    f"⏱️ {random.randint(30, 150)}ms\n\n"
                    f"📊 Score: {game['current_runs']}/{game.get('current_wickets', 0)}"
                )
                await message.reply_text(f"✅ Number {text} sent! You scored {runs} runs!")
                return
            else:
                await message.reply_text(
                    "❌ **Invalid input!**\n\n"
                    "Send a number between **1-6** to play the ball!"
                )
                return
    
    # Default response
    await message.reply_text(
        "🎮 **Cricket Game Bot**\n\n"
        "You are not in an active game session.\n\n"
        "Start a game with:\n"
        "• /solo_start - Play solo\n"
        "• /startgame - Create team match\n"
        "• /joingame - Join existing game"
    )
