from handlers.game import active_games
from database import db
from datetime import datetime
from config import RESULT_IMAGE_URL

async def end_match(client, message, chat_id):
    if chat_id not in active_games:
        return
    
    game = active_games[chat_id]
    current_runs = game.get("current_runs", 0)
    current_wickets = game.get("current_wickets", 0)
    current_balls = game.get("current_balls", 0)
    final_score = f"{current_runs}/{current_wickets}"
    
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
    
    # First message
    await client.send_message(
        chat_id,
        f"🏏 **Game Ended**\n\n"
        f"📊 Final Score: {final_score}\n"
        f"📈 Balls: {current_balls}\n\n"
        f"Result loading... 🎯"
    )
    
    # Second message with result image
    result_caption = f"─────⊱ 𝐒𝐨𝐥𝐨 𝐏𝐥𝐚𝐲𝐞𝐫𝐬 ⊰────\n\n{players_list}\n\n🎮 **Play Again:** /create_game"
    
    if RESULT_IMAGE_URL:
        await client.send_photo(chat_id, photo=RESULT_IMAGE_URL, caption=result_caption, parse_mode="HTML")
    else:
        await client.send_message(chat_id, result_caption, parse_mode="HTML")
    
    # Save to database
    await db.create_match({
        "chat_id": chat_id,
        "score": final_score,
        "balls": current_balls,
        "players": players,
        "created_at": datetime.now()
    })
    
    del active_games[chat_id]
