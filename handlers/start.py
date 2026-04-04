from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle  # ✅ ButtonStyle import karo
from database import db

# Aapki image ka link yahan daalo
IMAGE_URL = "https://files.catbox.moe/0odkk1.jpg"  # ⚠️ APNI IMAGE KA LINK DAALO

WELCOME_CAPTION = """
🏏 **𝐖ᴇʟᴄᴏᴍᴇ 𝐭ᴏ 𝐂ʀɪᴄᴋᴇᴛ 𝐁ᴏᴛ!**

🔴 **𝐋ɪᴠᴇ 𝐂ʀɪᴄᴋᴇᴛ 𝐒ᴄᴏʀᴇs:** Get real-time updates on live matches. Use /matches to see live scores.

🎮 **𝐌ᴀɴᴀɢᴇ 𝐘ᴏᴜʀ 𝐓ᴇᴀᴍ:** Strategize, set your lineup, and play the game just like a pro captain.

🗽 **1_VS_1:** Find one vs one match /1v1

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
    
    # ✅ Buttons with ButtonStyle
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏏 PLAY ZONE", callback_data="play_zone", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("📊 LIVE SCORE", callback_data="live_score", style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("📢 UPDATES", callback_data="updates", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("❓ HELP", callback_data="help_menu", style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("🔗 SUPPORT", callback_data="support", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("➕ ADD ME TO GROUP", callback_data="add_to_group", style=ButtonStyle.SUCCESS)
        ]
    ])
    
    # Agar image link hai toh photo bhejo, nahi toh sirf text
    if IMAGE_URL and IMAGE_URL != "https://telegra.ph/file/your-image-link.jpg":
        await message.reply_photo(
            photo=IMAGE_URL,
            caption=WELCOME_CAPTION,
            reply_markup=buttons
        )
    else:
        await message.reply_text(
            WELCOME_CAPTION,
            reply_markup=buttons
        )

async def host_callback(callback_query):
    """Host selection callback handler"""
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 I'm the Host", callback_data="host_selected", style=ButtonStyle.PRIMARY)]
    ])
    await callback_query.message.edit_text(
        "🎮 **New Game Alert!**\n\nWho will be the game host for this match?",
        reply_markup=buttons
    )
    await callback_query.answer()
