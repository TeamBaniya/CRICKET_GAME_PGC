from pyrogram.types import Message
import random
from handlers.game import active_games
from config import BATTING_VIDEO_URL, SIX_VIDEO_URL, FOUR_VIDEO_URL, WICKET_VIDEO_URL, OUT_VIDEO_URL

bowler_number_store = {}

async def batting_command(client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if chat_id not in active_games:
        await message.reply_text("❌ No active game found!")
        return
    
    game = active_games[chat_id]
    if game.get("current_batter") != user_id:
        await message.reply_text("❌ You are not the batter!")
        return
    
    await send_batting_screen(client, chat_id, message.from_user.first_name)

async def send_batting_screen(client, chat_id, batter_name):
    game = active_games[chat_id]
    game["batting_status"] = "waiting_for_number"
    
    ratings_text = "ND BAT 66 | MENTAL 66 | PACE 63 | PHYSICAL 66"
    
    await client.send_message(
        chat_id,
        f"🏏 **Now Batter: {batter_name} can send number (1-6)!!**\n\n"
        f"📊 **Ratings:** {ratings_text}\n\n"
        f"Type your number (1-6) in this group!"
    )
    
    if BATTING_VIDEO_URL:
        await client.send_video(chat_id, BATTING_VIDEO_URL)

async def handle_group_batting_number(client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    number = int(message.text.strip())
    
    try:
        await message.react(emoji="👍")
    except:
        pass
    
    if chat_id not in active_games:
        return
    
    game = active_games[chat_id]
    if game.get("current_batter") != user_id:
        await message.reply_text("❌ You are not the current batsman!")
        return
    
    if game.get("batting_status") != "waiting_for_number":
        return
    
    from handlers.bowling import bowler_number_store
    bowler_num = bowler_number_store.get(chat_id, 0)
    
    # CHECK IF OUT (Numbers match)
    if bowler_num == number and bowler_num != 0:
        game["current_wickets"] = game.get("current_wickets", 0) + 1
        game["current_balls"] = game.get("current_balls", 0) + 1
        game["batting_status"] = "completed"
        
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
            f"📊 Score: {game.get('current_runs', 0)}/{game['current_wickets']}\n"
            f"⏱️ {response_time}ms\n\n"
            f"Bowler: {bowler_num} | Batter: {number}"
        )
        
        bowler_number_store[chat_id] = 0
        
        # Check for match end
        total_balls = game.get('total_balls', 12)
        if game.get('current_balls', 0) >= total_balls or game.get('current_wickets', 0) >= 10:
            from handlers.result import end_match
            await end_match(client, message, chat_id)
            return
        
        # Switch to next batsman
        players = game.get("players", [])
        current_batter_index = game.get("current_batter_index", 0)
        next_index = current_batter_index + 1
        
        if next_index < len(players):
            game["current_batter"] = players[next_index]["user_id"]
            game["current_batter_index"] = next_index
            game["batting_status"] = "waiting_for_number"
            await client.send_message(
                chat_id,
                f"🔄 **Hey {players[next_index]['first_name']}, now you're batting!**\n\n"
                f"Send your number (1-6) in group to play!"
            )
        else:
            from handlers.result import end_match
            await end_match(client, message, chat_id)
        return
    
    # NOT OUT - Add runs
    runs = number
    game["current_runs"] = game.get("current_runs", 0) + runs
    game["current_balls"] = game.get("current_balls", 0) + 1
    game["batting_status"] = "completed"
    
    if runs == 6 and SIX_VIDEO_URL:
        await client.send_video(chat_id, SIX_VIDEO_URL, caption=f"🎯 **SIX!** 🚀")
    elif runs == 4 and FOUR_VIDEO_URL:
        await client.send_video(chat_id, FOUR_VIDEO_URL, caption=f"🎯 **FOUR!** 💥")
    
    response_time = random.randint(30, 150)
    await message.reply_text(
        f"🏏 **{runs} RUN{'S' if runs > 1 else ''}!**\n\n"
        f"📊 Score: {game['current_runs']}/{game.get('current_wickets', 0)}\n"
        f"📈 Balls: {game['current_balls']}/{game.get('total_balls', 12)}\n"
        f"⏱️ {response_time}ms\n\n"
        f"Bowler: {bowler_num} | Batter: {number}"
    )
    
    bowler_number_store[chat_id] = 0
    
    total_balls = game.get('total_balls', 12)
    if game.get('current_balls', 0) >= total_balls or game.get('current_wickets', 0) >= 10:
        from handlers.result import end_match
        await end_match(client, message, chat_id)
        return
    
    # Next ball - ask bowler
    game["bowling_status"] = "waiting_for_number"
    game["batting_status"] = "waiting_for_number"
    await client.send_message(chat_id, f"🔄 **Next ball! Bowler, click the BOWLING button!**")
