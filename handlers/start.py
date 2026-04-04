from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db

WELCOME_MESSAGE = """
🏏 **CRICKET CHAMPIONSHIP** 🏏

**WELCOME TO CRICKET BOT!**

• **LIVE CRICKET SCORES:** Get real-time updates on live matches.
• **MANAGE YOUR TEAM:** Strategize, set your lineup, and play the game.
• **1_VS_1:** Find one vs one match /1v1

Use /help to learn more about the game.
"""

async def start_command(client, message: Message):
    user = message.from_user
    
    await db.save_user({
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "state": "MAIN_MENU"
    })
    
    # Main menu buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏏 PLAY ZONE", callback_data="play_zone"),
            InlineKeyboardButton("📊 LIVE SCORE", callback_data="live_score")
        ],
        [
            InlineKeyboardButton("📢 UPDATES", callback_data="updates"),
            InlineKeyboardButton("❓ HELP", callback_data="help_menu")
        ],
        [
            InlineKeyboardButton("🔗 SUPPORT", callback_data="support"),
            InlineKeyboardButton("➕ ADD ME TO GROUP", callback_data="add_to_group")
        ]
    ])
    
    await message.reply_text(WELCOME_MESSAGE, reply_markup=buttons)

async def host_callback(callback_query):
    """Host selection callback handler"""
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 I'm the Host", callback_data="host_selected")]
    ])
    await callback_query.message.edit_text(
        "🎮 **New Game Alert!**\n\nWho will be the game host for this match?",
        reply_markup=buttons
    )
    await callback_query.answer()
