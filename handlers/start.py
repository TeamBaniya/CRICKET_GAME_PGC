from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db

# ========== YAHAN SIRF YE 4 LINKS BADALNI HAIN ==========
IMAGE_URL = "https://files.catbox.moe/0odkk1.jpg"  # Aapki image ka link (set hai)

# In teeno links ko apne channel/group links se replace karein
UPDATES_LINK = "https://t.me/your_updates_channel"      # 📢 UPDATES button ke liye
SUPPORT_LINK = "https://t.me/your_support_group"        # 🔗 SUPPORT button ke liye
PLAYZONE_LINK = "https://t.me/your_playzone_group"      # 🏏 PLAY ZONE button ke liye
# =======================================================

WELCOME_CAPTION = """
🏏 **𝐖ᴇʟᴄᴏᴍᴇ 𝐭ᴏ 𝐂ʀɪᴄᴋᴇᴛ 𝐁ᴏᴛ!**

🔴 **𝐋ɪᴠᴇ 𝐂ʀɪᴄᴋᴇᴛ 𝐒ᴄᴏʀᴇs:** Get real-time updates on live matches. Use /matches to see live scores.

🎮 **𝐌ᴀɴᴀɢᴇ 𝐘ᴏᴜʀ 𝐓ᴇᴀᴍ:** Strategize, set your lineup, and play the game just like a pro captain.

🗽 **1_VS_1:** Find one vs one match /1v1

Use /help to learn more about the game.
"""

async def start_command(client, message: Message):
    user = message.from_user

    # User ko database mein save karna
    await db.save_user({
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "state": "MAIN_MENU"
    })

    # 🔘 Buttons with Actions and Styles
    buttons = InlineKeyboardMarkup([
        [
            # PLAY ZONE ab ek GROUP LINK kholega
            InlineKeyboardButton("🏏 PLAY ZONE", url=PLAYZONE_LINK, style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("📊 LIVE SCORE", callback_data="live_score", style=ButtonStyle.DEFAULT)
        ],
        [
            # UPDATES ab ek CHANNEL LINK kholega
            InlineKeyboardButton("📢 UPDATES", url=UPDATES_LINK, style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("❓ HELP", callback_data="help_menu", style=ButtonStyle.DEFAULT)
        ],
        [
            # SUPPORT ab ek GROUP LINK kholega
            InlineKeyboardButton("🔗 SUPPORT", url=SUPPORT_LINK, style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("➕ ADD ME TO GROUP", callback_data="add_to_group", style=ButtonStyle.SUCCESS)
        ]
    ])

    # 🖼️ Image aur caption bhejna
    await message.reply_photo(
        photo=IMAGE_URL,
        caption=WELCOME_CAPTION,
        reply_markup=buttons
    )


async def host_callback(callback_query):
    """Callback for 'I'm the Host' button (used elsewhere)"""
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 I'm the Host", callback_data="host_selected", style=ButtonStyle.PRIMARY)]
    ])
    await callback_query.message.edit_text(
        "🎮 **New Game Alert!**\n\nWho will be the game host for this match?",
        reply_markup=buttons
    )
    await callback_query.answer()
