# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle

AUCTION_MESSAGE = """
💰 **AUCTION COMMANDS**

/add_cap - add auction captain
/rm_cap - remove auction captain
/cap_change_auction - change auction captain
/auction_id - send auction player ID
/start_auction - start auction 🎉
/pause_auction - pause auction 📊
/resume_auction - resume auction
/auction_host_change - change auction host 🏆
/xp - auction player put value 💰
/unhold - auction player unsold list
/rm_auction_id - remove auction sold player ❌
"""

async def add_cap_command(client, message: Message):
    await message.reply_text("✅ Auction captain added!")

async def rm_cap_command(client, message: Message):
    await message.reply_text("❌ Auction captain removed!")

async def cap_change_command(client, message: Message):
    await message.reply_text("🔄 Auction captain changed!")

async def auction_id_command(client, message: Message):
    await message.reply_text("📋 Auction Player ID: \nSend player ID to start bidding")

async def start_auction_command(client, message: Message):
    await message.reply_text("🎉 Auction Started! Place your bids using /xp")

async def pause_auction_command(client, message: Message):
    await message.reply_text("⏸️ Auction Paused! Use /resume_auction to continue")

async def resume_auction_command(client, message: Message):
    await message.reply_text("▶️ Auction Resumed!")

async def auction_host_change_command(client, message: Message):
    await message.reply_text("🏆 Auction host changed!")

async def xp_command(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Usage: /xp <amount>\nPut your bid value!")
        return
    await message.reply_text(f"💰 Bid placed: {args[1]} coins!")

async def unhold_command(client, message: Message):
    await message.reply_text("📋 Unsold players list:\n• Player 1\n• Player 2")

async def rm_auction_id_command(client, message: Message):
    await message.reply_text("❌ Auction player removed from sold list!")

async def auction_mode_menu(callback_query):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)]
    ])
    await callback_query.message.edit_text(AUCTION_MESSAGE, reply_markup=buttons)
