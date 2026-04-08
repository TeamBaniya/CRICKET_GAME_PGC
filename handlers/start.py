from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from pyrogram import Client, filters

from database import db
from config import (
    IMAGE_URL,
    WELCOME_CAPTION,
    UPDATES_LINK,
    SUPPORT_LINK,
    PLAYZONE_LINK,
    LIVE_SCORE_LINK
)


# ==================== START COMMAND ====================

@Client.on_message(filters.private & filters.command("start"))
async def start_command(client, message: Message):
    user = message.from_user
    text = message.text

    # ==================== 🔥 BOWLING DEEP LINK ====================
    if "bowling_" in text:
        chat_id = text.split("bowling_")[1]

        # Group link convert
        group_link = f"https://t.me/c/{str(chat_id).replace('-100','')}"

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 BACK TO GROUP",
                    url=group_link,
                    style=ButtonStyle.PRIMARY
                )
            ]
        ])

        await message.reply_text(
            "🎯 **Send your bowling number (1-6)!**\n\n"
            "⏰ You have 60 seconds!\n\n"
            "👉 Send only number (1-6)",
            reply_markup=buttons
        )
        return

    # ==================== NORMAL START ====================

    # Save user in DB
    await db.save_user({
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "state": "MAIN_MENU"
    })

    # Buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏏 PLAY ZONE", url=PLAYZONE_LINK, style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("📊 LIVE SCORE", url=LIVE_SCORE_LINK, style=ButtonStyle.DANGER)
        ],
        [
            InlineKeyboardButton("📢 UPDATES", url=UPDATES_LINK, style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🔗 SUPPORT", url=SUPPORT_LINK, style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("➕ ADD ME TO GROUP", callback_data="add_to_group", style=ButtonStyle.DANGER)
        ]
    ])

    # Send welcome image
    await message.reply_photo(
        photo=IMAGE_URL,
        caption=WELCOME_CAPTION,
        reply_markup=buttons
    )


# ==================== ADD TO GROUP ====================

@Client.on_callback_query(filters.regex("add_to_group"))
async def add_to_group_callback(client, callback_query):
    bot_username = (await client.get_me()).username

    await callback_query.message.edit_text(
        "➕ **ADD ME TO YOUR GROUP**\n\n"
        "1. Add me to your group\n"
        f"👉 https://t.me/{bot_username}?startgroup=true\n\n"
        "2. Make me admin (important!)\n\n"
        "3. Type /start in group\n\n"
        "4. Start playing with friends! 🏏"
    )

    await callback_query.answer()
