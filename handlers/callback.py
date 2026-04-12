from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from handlers.help import game_instructions_menu, solo_mode_menu, back_to_game_instructions, team_mode_menu, help_command
from handlers.auction import auction_mode_menu
from handlers.match import overs_selected
from handlers.start import start_command, add_to_group_callback
from config import UPDATES_LINK, SUPPORT_LINK

async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    print(f"🔵 DEBUG: callback_handler called with data: {data}")
    await callback_query.answer()
    
    # ========== MAIN MENU NAVIGATION ==========
    if data == "play_zone":
        await game_instructions_menu(callback_query)
    
    elif data == "live_score":
        await callback_query.message.edit_text(
            "📊 **LIVE SCORES**\n\n"
            "No live matches currently.\n\n"
            "Start a match with /startgame"
        )
    
    elif data == "updates":
        await callback_query.message.edit_text(
            f"📢 **UPDATES**\n\n"
            f"[Join Updates Channel]({UPDATES_LINK}) for latest news!"
        )
    
    elif data == "help_menu":
        class FakeMessage:
            def __init__(self, chat, from_user, edit_text):
                self.chat = chat
                self.from_user = from_user
                self.reply_text = edit_text
        fake_msg = FakeMessage(
            callback_query.message.chat,
            callback_query.from_user,
            callback_query.message.edit_text
        )
        await help_command(client, fake_msg)
    
    elif data == "support":
        await callback_query.message.edit_text(
            f"🔗 **SUPPORT**\n\n"
            f"[Join Support Group]({SUPPORT_LINK}) for help!"
        )
    
    elif data == "add_to_group":
        await add_to_group_callback(callback_query)
    
    elif data == "developer":
        await callback_query.message.edit_text(
            "👨‍💻 **DEVELOPER**\n\n"
            "Bot by @developer\n\n"
            "For queries contact @developer"
        )
    
    # ========== GAME INSTRUCTIONS ==========
    elif data == "game_instructions":
        await game_instructions_menu(callback_query)
    
    # ========== GAME MODES ==========
    elif data == "solo_mode" or data == "solo_play":
        await solo_mode_menu(callback_query)
    
    elif data == "team_mode" or data == "team_play":
        await team_mode_menu(callback_query)
    
    elif data == "auction_mode" or data == "auction":
        await auction_mode_menu(callback_query)
    
    # ========== CREATE GAME CALLBACKS ==========
    elif data == "create_solo":
        from handlers.game import create_solo_game
        await create_solo_game(callback_query)
    
    elif data == "create_team":
        from handlers.game import create_team_game
        await create_team_game(callback_query)
    
    # ========== SOLO MATCH START CALLBACK ==========
    elif data == "start_solo_match":
        from handlers.game import start_solo_match_callback
        await start_solo_match_callback(callback_query)
    
    # ========== BOWLING BUTTON CALLBACK ==========
    elif data == "bowling_btn":
        print("🔵 DEBUG: bowling_btn callback received, calling bowling_button_callback")
        from handlers.gameplay import bowling_button_callback
        await bowling_button_callback(callback_query)
    
    # ========== BOWLER NUMBER BUTTONS (1-6) ==========
    elif data.startswith("bowler_number_"):
        number = int(data.split("_")[2])
        user_id = callback_query.from_user.id
        chat_id = None
        
        from handlers.gameplay import active_games, bowler_number_store
        for cid, game in active_games.items():
            if game.get("current_bowler") == user_id:
                chat_id = cid
                break
        
        if chat_id and chat_id in active_games:
            game = active_games[chat_id]
            if game.get("bowling_status") == "waiting_for_number":
                game["bowling_status"] = "completed"
                bowler_number_store[chat_id] = number
                
                # Send batting screen to group
                await callback_query._client.send_message(
                    chat_id,
                    f"🎯 **Bowler has sent their number!**\n\n"
                    f"Now batsman, send your number (1-6) in group!"
                )
                await callback_query.message.edit_text(f"✅ You selected {number}! Waiting for batsman...")
                await callback_query.answer(f"Number {number} sent!")
                
                # Call batting screen
                from handlers.dm_handler import send_batting_screen_to_group
                await send_batting_screen_to_group(callback_query._client, chat_id, game)
            else:
                await callback_query.answer("Already processed!", show_alert=True)
        else:
            await callback_query.answer("No active game!", show_alert=True)
    
    # ========== BOWLER BACK TO GROUP BUTTON ==========
    elif data == "bowler_back_to_group":
        user_id = callback_query.from_user.id
        chat_id = None
        
        from handlers.gameplay import active_games
        for cid, game in active_games.items():
            if game.get("current_bowler") == user_id:
                chat_id = cid
                break
        
        if chat_id:
            await callback_query._client.send_message(
                chat_id,
                f"🎯 **@{callback_query.from_user.first_name}, send your bowling number (1-6) in group!**"
            )
            await callback_query.message.edit_text("✅ Returned to group! Send your number there.")
        else:
            await callback_query.message.edit_text("❌ No active game found!")
        
        await callback_query.answer()
    
    # ========== BATTING BUTTON CALLBACK ==========
    elif data == "batting_btn":
        await callback_query.answer("Batting button clicked! Send number in group!")
    
    # ========== OVERS SELECTION ==========
    elif data.startswith("overs_"):
        overs = int(data.split("_")[1])
        await overs_selected(callback_query, overs)
    
    # ========== NAVIGATION ==========
    elif data == "home":
        class FakeMessage:
            def __init__(self, chat, from_user, edit_text):
                self.chat = chat
                self.from_user = from_user
                self.reply_text = edit_text
        fake_msg = FakeMessage(
            callback_query.message.chat,
            callback_query.from_user,
            callback_query.message.edit_text
        )
        await help_command(client, fake_msg)
    
    elif data == "back":
        await game_instructions_menu(callback_query)
    
    elif data == "back_to_instructions":
        await game_instructions_menu(callback_query)
    
    elif data == "back_to_match":
        await callback_query.message.edit_text(
            "🏏 **Match**\n\n"
            "Use /bowling command to continue the game."
        )
    
    elif data == "back_to_main":
        class FakeMessage:
            def __init__(self, chat, from_user, edit_text):
                self.chat = chat
                self.from_user = from_user
                self.reply_text = edit_text
        fake_msg = FakeMessage(
            callback_query.message.chat,
            callback_query.from_user,
            callback_query.message.edit_text
        )
        await start_command(client, fake_msg)
    
    elif data == "back_to_game_instructions":
        await back_to_game_instructions(callback_query)
    
    # ========== AUCTION CALLBACKS ==========
    elif data == "auction_bid":
        from handlers.auction import auction_bid_callback
        await auction_bid_callback(callback_query)
    
    elif data == "auction_pause":
        from handlers.auction import auction_pause_callback
        await auction_pause_callback(callback_query)
    
    elif data == "auction_skip":
        from handlers.auction import auction_skip_callback
        await auction_skip_callback(callback_query)
    
    # ========== DEFAULT ==========
    else:
        print(f"🔴 DEBUG: Unknown callback data: {data}")
        await callback_query.message.edit_text(
            "⚠️ **Feature coming soon!**\n\n"
            "This feature is under development."
        )
