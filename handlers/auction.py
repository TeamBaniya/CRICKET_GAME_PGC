# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from datetime import datetime

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

# Store active auction sessions
active_auctions = {}

async def add_cap_command(client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if auction exists
    if chat_id not in active_auctions:
        active_auctions[chat_id] = {
            "captain": None,
            "players": [],
            "status": "waiting",
            "host": user_id
        }
    
    active_auctions[chat_id]["captain"] = user_id
    await message.reply_text(f"✅ {message.from_user.first_name} is now the auction captain!")

async def rm_cap_command(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in active_auctions:
        active_auctions[chat_id]["captain"] = None
        await message.reply_text("❌ Auction captain removed!")
    else:
        await message.reply_text("❌ No active auction found!")

async def cap_change_command(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Usage: /cap_change_auction @username")
        return
    
    chat_id = message.chat.id
    new_captain = args[1].replace("@", "")
    
    if chat_id in active_auctions:
        active_auctions[chat_id]["captain"] = new_captain
        await message.reply_text(f"🔄 Auction captain changed to @{new_captain}!")
    else:
        await message.reply_text("❌ No active auction found!")

async def auction_id_command(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("📋 **Auction Player ID**\n\nSend player ID to start bidding\n\nUsage: /auction_id <player_id>")
        return
    
    player_id = args[1]
    chat_id = message.chat.id
    
    if chat_id not in active_auctions:
        active_auctions[chat_id] = {
            "captain": None,
            "players": [],
            "status": "waiting",
            "host": message.from_user.id
        }
    
    active_auctions[chat_id]["current_player"] = player_id
    active_auctions[chat_id]["current_bid"] = 0
    active_auctions[chat_id]["current_bidder"] = None
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 Place Bid", callback_data="auction_bid", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⏸️ Pause", callback_data="auction_pause", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("❌ Skip", callback_data="auction_skip", style=ButtonStyle.DANGER)
        ]
    ])
    
    await message.reply_text(
        f"🎯 **Player {player_id} is up for auction!**\n\n"
        f"Starting bid: 0 coins\n"
        f"Use /xp <amount> to place bid\n"
        f"⏰ Timer: 30 seconds",
        reply_markup=buttons
    )

async def start_auction_command(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id not in active_auctions:
        active_auctions[chat_id] = {
            "captain": None,
            "players": [],
            "status": "live",
            "host": message.from_user.id,
            "start_time": datetime.now()
        }
    else:
        active_auctions[chat_id]["status"] = "live"
        active_auctions[chat_id]["start_time"] = datetime.now()
    
    await message.reply_text(
        "🎉 **AUCTION STARTED!** 🎉\n\n"
        "Use /auction_id <player_id> to put a player for auction\n"
        "Use /xp <amount> to place bids\n\n"
        "Let the bidding begin! 💰"
    )

async def pause_auction_command(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in active_auctions:
        active_auctions[chat_id]["status"] = "paused"
        await message.reply_text("⏸️ **Auction Paused!**\nUse /resume_auction to continue")
    else:
        await message.reply_text("❌ No active auction found!")

async def resume_auction_command(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in active_auctions:
        active_auctions[chat_id]["status"] = "live"
        await message.reply_text("▶️ **Auction Resumed!**\n\nUse /auction_id to continue bidding")
    else:
        await message.reply_text("❌ No active auction found!")

async def auction_host_change_command(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Usage: /auction_host_change @username")
        return
    
    chat_id = message.chat.id
    new_host = args[1].replace("@", "")
    
    if chat_id in active_auctions:
        active_auctions[chat_id]["host"] = new_host
        await message.reply_text(f"🏆 Auction host changed to @{new_host}!")
    else:
        await message.reply_text("❌ No active auction found!")

async def xp_command(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Usage: /xp <amount>\nPut your bid value!")
        return
    
    try:
        bid_amount = int(args[1])
    except ValueError:
        await message.reply_text("❌ Please enter a valid number!")
        return
    
    chat_id = message.chat.id
    user = message.from_user
    
    if chat_id not in active_auctions:
        await message.reply_text("❌ No active auction found!")
        return
    
    auction = active_auctions[chat_id]
    
    if auction.get("status") != "live":
        await message.reply_text("❌ Auction is not live right now!")
        return
    
    if bid_amount <= auction.get("current_bid", 0):
        await message.reply_text(f"❌ Bid must be higher than current bid ({auction['current_bid']} coins)!")
        return
    
    auction["current_bid"] = bid_amount
    auction["current_bidder"] = user.id
    
    await message.reply_text(
        f"💰 **Bid placed!**\n\n"
        f"Bidder: {user.first_name}\n"
        f"Amount: {bid_amount} coins\n\n"
        f"Current highest bid: {bid_amount} coins"
    )

async def unhold_command(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in active_auctions and "unsold_players" in active_auctions[chat_id]:
        unsold = active_auctions[chat_id]["unsold_players"]
        if unsold:
            players_list = "\n".join([f"• {p}" for p in unsold])
            await message.reply_text(f"📋 **Unsold players list:**\n\n{players_list}")
        else:
            await message.reply_text("📋 No unsold players!")
    else:
        await message.reply_text("📋 No unsold players found!")

async def rm_auction_id_command(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Usage: /rm_auction_id <player_id>\nRemove auction sold player!")
        return
    
    player_id = args[1]
    chat_id = message.chat.id
    
    if chat_id in active_auctions:
        if "sold_players" not in active_auctions[chat_id]:
            active_auctions[chat_id]["sold_players"] = []
        
        if player_id in active_auctions[chat_id]["sold_players"]:
            active_auctions[chat_id]["sold_players"].remove(player_id)
            await message.reply_text(f"❌ Player {player_id} removed from sold list!")
        else:
            await message.reply_text(f"❌ Player {player_id} not found in sold list!")
    else:
        await message.reply_text("❌ No active auction found!")

async def auction_mode_menu(callback_query):
    """Auction menu with back button"""
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)]
    ])
    await callback_query.message.edit_text(AUCTION_MESSAGE, reply_markup=buttons)
    await callback_query.answer()


async def auction_bid_callback(callback_query):
    """Place bid button callback"""
    await callback_query.message.reply_text(
        "💰 **Place your bid**\n\n"
        "Use /xp <amount> to place your bid\n"
        "Example: /xp 1000"
    )
    await callback_query.answer()


async def auction_pause_callback(callback_query):
    """Pause auction button callback"""
    chat_id = callback_query.message.chat.id
    if chat_id in active_auctions:
        active_auctions[chat_id]["status"] = "paused"
        await callback_query.message.edit_text(
            "⏸️ **Auction Paused!**\n\n"
            "Use /resume_auction to continue"
        )
    await callback_query.answer()


async def auction_skip_callback(callback_query):
    """Skip current player button callback"""
    chat_id = callback_query.message.chat.id
    if chat_id in active_auctions:
        current_player = active_auctions[chat_id].get("current_player")
        if current_player:
            if "unsold_players" not in active_auctions[chat_id]:
                active_auctions[chat_id]["unsold_players"] = []
            active_auctions[chat_id]["unsold_players"].append(current_player)
            
            await callback_query.message.edit_text(
                f"❌ Player {current_player} went unsold!\n\n"
                f"Use /auction_id to put next player"
            )
    await callback_query.answer()
