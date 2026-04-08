# TODO: Add your code here
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from handlers.help import game_instructions_menu, solo_mode_menu, back_to_game_instructions, team_mode_menu, help_command
from handlers.auction import auction_mode_menu
from handlers.match import overs_selected
from handlers.start import start_command, add_to_group_callback
from config import BOWLING_SPEEDS_BUTTONS, UPDATES_LINK, SUPPORT_LINK

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
    
    # ========== OVERS SELECTION ==========
    elif data.startswith("overs_"):
        overs = int(data.split("_")[1])
        await overs_selected(callback_query, overs)
    
    # ========== BOWLING SPEEDS ==========
    elif data.upper() in [s.upper() for s in BOWLING_SPEEDS_BUTTONS]:
        from handlers.gameplay import bowling_speed_selected
        await bowling_speed_selected(callback_query, data.upper())
    
    # ========== BATTING ACTIONS ==========
    elif data == "timing":
        from handlers.gameplay import timing_selected
        await timing_selected(callback_query)
    
    elif data == "direction":
        from handlers.gameplay import direction_selected
        await direction_selected(callback_query)
    
    elif data == "take_run":
        from handlers.gameplay import take_run_selected
        await take_run_selected(callback_query)
    
    # ========== BOWLING/BATTING SELECT ==========
    elif data == "bowling_select":
        from handlers.gameplay import show_bowling_speed_options
        await show_bowling_speed_options(callback_query)
    
    elif data == "batting_select":
        from handlers.gameplay import show_batting_ratings
        await show_batting_ratings(callback_query)
    
    # ========== TEAM MODE VIDEO CALLBACKS ==========
    elif data == "team_start":
        from config import TEAM_START_VIDEO_URL
        await callback_query.message.reply_video(
            video=TEAM_START_VIDEO_URL,
            caption="🎮 **START**\n\nUse /add_A and /add_B to add players to teams."
        )
    
    elif data == "team_add":
        from config import TEAM_ADD_VIDEO_URL
        await callback_query.message.reply_video(
            video=TEAM_ADD_VIDEO_URL,
            caption="➕ **ADD MEMBERS**\n\n/add_A @username - Add to Team A\n/add_B @username - Add to Team B"
        )
    
    elif data == "team_remove":
        from config import TEAM_REMOVE_VIDEO_URL
        await callback_query.message.reply_video(
            video=TEAM_REMOVE_VIDEO_URL,
            caption="❌ **REMOVE MEMBERS**\n\n/remove_A <number> - Remove from Team A\n/remove_B <number> - Remove from Team B"
        )
    
    elif data == "team_startgame":
        from config import TEAM_STARTGAME_VIDEO_URL
        await callback_query.message.reply_video(
            video=TEAM_STARTGAME_VIDEO_URL,
            caption="🏏 **START GAME**\n\nUse /startgame to begin the match after teams are ready!"
        )
    
    elif data == "team_bowling":
        from config import TEAM_BOWLING_VIDEO_URL
        await callback_query.message.reply_video(
            video=TEAM_BOWLING_VIDEO_URL,
            caption="🎯 **BOWLING**\n\n/bowling <speed> - Select bowling speed\nExample: /bowling FAST"
        )
    
    elif data == "team_batting":
        from config import TEAM_BATTING_VIDEO_URL
        await callback_query.message.reply_video(
            video=TEAM_BATTING_VIDEO_URL,
            caption="🏏 **BATTING**\n\n/batting <number> - Play your shot\nExample: /batting 4"
        )
    
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
            "Use /bowling and /batting commands to continue the game."
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
    
    # ========== DEFAULT ==========
    else:
        await callback_query.message.edit_text(
            "⚠️ **Feature coming soon!**\n\n"
            "This feature is under development."
        )
