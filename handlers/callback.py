# TODO: Add your code here
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from handlers.help import game_instructions_menu, solo_mode_menu, back_to_game_instructions, team_mode_menu, help_command
from handlers.auction import auction_mode_menu
from handlers.match import overs_selected
from handlers.start import start_command, add_to_group_callback
from config import UPDATES_LINK, SUPPORT_LINK

async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    await callback_query.answer()  # Fast response
    
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
    
    # ========== BOWLING BUTTON - IGNORE (deep link used) ==========
    elif data == "bowling_btn":
        # Silent ignore - deep link already sent in group
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
        await callback_query.message.edit_text(
            "⚠️ **Feature coming soon!**\n\n"
            "This feature is under development."
        )
