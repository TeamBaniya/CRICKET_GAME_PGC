from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from handlers.solo import solo_start_multi
from handlers.match import startgame_command

async def create_game_command(client, message: Message):
    """/create_game command - Show game type selection"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Solo", callback_data="create_solo", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("👥 Team", callback_data="create_team", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("◀️ BACK", callback_data="back_to_main", style=ButtonStyle.DEFAULT)
        ]
    ])
    
    await message.reply_text(
        "🎮 **Create Game**\n\n"
        "Choose game type:",
        reply_markup=buttons
    )


async def create_solo_game(callback_query):
    """Create solo game (2 minutes join time)"""
    await callback_query.message.edit_text(
        "🎉 **Solo Game Created!** 🎉\n\n"
        "Join the game using `/joingame` (2 minutes to join)\n\n"
        "⏰ You have 2 minutes to join!"
    )
    await callback_query.answer()


async def create_team_game(callback_query):
    """Create team game"""
    await callback_query.message.edit_text(
        "👥 **Team Game Created!** 👥\n\n"
        "Join the game using `/joingame` (2 minutes to join)\n\n"
        "⏰ You have 2 minutes to join!"
    )
    await callback_query.answer()
