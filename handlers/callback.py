# TODO: Add your code here
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from handlers.help import game_instructions_menu
from handlers.team import team_mode_menu
from handlers.auction import auction_mode_menu
from handlers.match import overs_selected
from handlers.start import start_command

async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    await callback_query.answer()  # Fast response
    
    # Main menu navigation
    if data == "play_zone":
        await game_instructions_menu(callback_query)
    
    elif data == "live_score":
        await callback_query.message.edit_text("📊 **LIVE SCORES**\n\nNo live matches currently.")
    
    elif data == "updates":
        await callback_query.message.edit_text("📢 **UPDATES**\n\nJoin @cricket_updates for latest news!")
    
    elif data == "help_menu":
        from handlers.help import help_command
        class FakeMessage:
            def __init__(self, chat, from_user, reply_text):
                self.chat = chat
                self.from_user = from_user
                self.reply_text = reply_text
        fake_msg = FakeMessage(callback_query.message.chat, callback_query.from_user, callback_query.message.edit_text)
        await help_command(client, fake_msg)
    
    elif data == "support":
        await callback_query.message.edit_text("🔗 **SUPPORT**\n\nJoin @cricket_support for help!")
    
    elif data == "add_to_group":
        await callback_query.message.edit_text(
            "➕ **ADD ME TO YOUR GROUP**\n\n"
            "1. Add @cricket_bot to your group\n"
            "2. Make me admin\n"
            "3. Type /start in group"
        )
    
    elif data == "developer":
        await callback_query.message.edit_text("👨‍💻 **DEVELOPER**\n\nBot by @developer")
    
    elif data == "game_instructions":
        await game_instructions_menu(callback_query)
    
    # Game modes
    elif data == "solo_mode":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)]
        ])
        await callback_query.message.edit_text(
            "🎯 **SOLO MODE**\n\n/start - Begin solo match\n/joingame - Join match\n/end_match - End game",
            reply_markup=buttons
        )
    
    elif data == "team_mode":
        await team_mode_menu(callback_query)
    
    elif data == "auction_mode":
        await auction_mode_menu(callback_query)
    
    # Host selection
    elif data == "host_selected":
        await callback_query.message.edit_text(
            "🏏 **Team Creation**\n\n"
            "Team creation is underway!\n"
            "Join Team A: /join_teamA\n"
            "Join Team B: /join_teamB\n\n"
            "Check members: /members_list"
        )
    
    # Overs selection
    elif data.startswith("overs_"):
        overs = int(data.split("_")[1])
        await overs_selected(callback_query, overs)
    
    # Bowling/Batting
    elif data == "bowling_select":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏏 /batting", callback_data="batting_select", style=ButtonStyle.SUCCESS)],
            [InlineKeyboardButton("◀️ BACK", callback_data="back_to_match", style=ButtonStyle.DEFAULT)]
        ])
        await callback_query.message.edit_text(
            "Select bowler using /bowling <player_number>\n\nExample: /bowling 3",
            reply_markup=buttons
        )
    
    elif data == "batting_select":
        await callback_query.message.edit_text(
            "Select batsman using /batting <player_number>\n\nExample: /batting 4"
        )
    
    # Navigation
    elif data == "home":
        class FakeMessage:
            def __init__(self, chat, from_user, reply_text):
                self.chat = chat
                self.from_user = from_user
                self.reply_text = reply_text
        fake_msg = FakeMessage(callback_query.message.chat, callback_query.from_user, callback_query.message.edit_text)
        await start_command(client, fake_msg)
    
    elif data == "back_to_instructions":
        await game_instructions_menu(callback_query)
    
    elif data == "back_to_match":
        await callback_query.message.edit_text(
            "🏏 **Match**\n\nUse /bowling and /batting commands"
        )
