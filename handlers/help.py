# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle

HELP_MESSAGE = """
Hello! 🎉 Need some help with Cricket Master Bot?

• **Join a Match:** Type /start in groups
• **Manage Your Team:** Use /startgame to get started
• **Game Instructions:** Click below button
• **Feedback:** Share your /feedback

Enjoy your time with Cricket Master Bot! 🎉
"""

GAME_INSTRUCTIONS_MESSAGE = """
🎮 **GAME INSTRUCTIONS**

Choose your mode to play:
"""

async def help_command(client, message: Message):
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ ADD ME TO GROUP", callback_data="add_to_group", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🎮 Game Instructions", callback_data="game_instructions", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("📢 UPDATES", callback_data="updates", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("🔗 SUPPORT", callback_data="support", style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("👨‍💻 DEVELOPER", callback_data="developer", style=ButtonStyle.DEFAULT)
        ]
    ])
    await message.reply_text(HELP_MESSAGE, reply_markup=buttons)

async def game_instructions_menu(callback_query):
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Solo Play", callback_data="solo_mode", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("👥 Team Play", callback_data="team_mode", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("💰 Auction", callback_data="auction_mode", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🏠 Home", callback_data="home", style=ButtonStyle.DEFAULT)
        ]
    ])
    await callback_query.message.edit_text(
        GAME_INSTRUCTIONS_MESSAGE,
        reply_markup=buttons
    )
