# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db

async def bowling_command(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Usage: /bowling 3\n(Use team A or B player number)")
        return
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏏 /batting", callback_data="batting_select", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("◀️ BACK", callback_data="back_to_match", style=ButtonStyle.DEFAULT)]
    ])
    
    await message.reply_text(
        f"✅ Bowler {args[1]} selected!\n\nNow, type /batting to choose the batting member!",
        reply_markup=buttons
    )

async def batting_command(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Usage: /batting 4\n(Use team A or B player number)")
        return
    
    await message.reply_text(f"✅ Batsman {args[1]} selected!\n\n🏏 Match started! Let's play!")

async def swap_command(client, message: Message):
    await message.reply_text("🔄 Playing position swapped!")

async def end_match_command(client, message: Message):
    await message.reply_text("🏆 Match Ended! Thanks for playing!")
