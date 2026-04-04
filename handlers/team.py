# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db

TEAM_MODE_MESSAGE = """
👥 **TEAM MODE COMMANDS**

**ADD MEMBERS:**
/add_A - add members to team A
/add_B - add members to team B

**REMOVE MEMBERS:**
/remove_A - remove members from team A
/remove_B - remove members from team B

**GAME PLAY:**
/startgame - to start the game
/bowling - choose the bowling person
/batting - choose the batting person
/swap - change playing position
/end_match - end the current game
"""

async def add_a_command(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Usage: /add_A @username or /add_A 1")
        return
    # Logic to add to team A
    await message.reply_text(f"✅ Player {args[1]} added to Team A!")

async def add_b_command(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Usage: /add_B @username or /add_B 1")
        return
    await message.reply_text(f"✅ Player {args[1]} added to Team B!")

async def join_teama_command(client, message: Message):
    await message.reply_text(f"✅ {message.from_user.first_name} joined Team A!")

async def join_teamb_command(client, message: Message):
    await message.reply_text(f"✅ {message.from_user.first_name} joined Team B!")

async def members_list_command(client, message: Message):
    await message.reply_text("📋 **Current Members:**\nTeam A: \nTeam B: ")

async def team_mode_menu(callback_query):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)]
    ])
    await callback_query.message.edit_text(TEAM_MODE_MESSAGE, reply_markup=buttons)
