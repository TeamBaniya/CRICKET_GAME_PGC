# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db

OVERS_MESSAGE = """
🏏 **Cricket Game**

How many overs do you want for this game?
"""

async def startgame_command(client, message: Message):
    # Overs selection buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1 over", callback_data="overs_1", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("2 overs", callback_data="overs_2", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("3 overs", callback_data="overs_3", style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("4 overs", callback_data="overs_4", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("5 overs", callback_data="overs_5", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("6 overs", callback_data="overs_6", style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("7 overs", callback_data="overs_7", style=ButtonStyle.DEFAULT)
        ]
    ])
    await message.reply_text(OVERS_MESSAGE, reply_markup=buttons)

async def overs_selected(callback_query, overs):
    await db.save_session({
        "match_id": str(callback_query.message.chat.id),
        "overs": overs,
        "status": "ready"
    })
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 /bowling", callback_data="bowling_select", style=ButtonStyle.PRIMARY)]
    ])
    
    await callback_query.message.edit_text(
        f"🎉 OHOO! 👏 Let's play a {overs} overs Match!!\n\nTeam B will bowl first!\n\nNow, type /bowling to choose the bowling member!",
        reply_markup=buttons
    )
