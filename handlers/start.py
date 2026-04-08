from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from config import IMAGE_URL, WELCOME_CAPTION, UPDATES_LINK, SUPPORT_LINK, PLAYZONE_LINK, LIVE_SCORE_LINK

async def start_command(client, message: Message):
    user = message.from_user

    # User ko database mein save karna
    await db.save_user({
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "state": "MAIN_MENU"
    })

    # 🔘 Buttons - Sab direct links (ADD TO GROUP callback hai)
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

    # 🖼️ Image aur caption bhejna
    await message.reply_photo(
        photo=IMAGE_URL,
        caption=WELCOME_CAPTION,
        reply_markup=buttons
    )


async def add_to_group_callback(callback_query):
    """Add to group button callback"""
    bot_username = (await callback_query._client.get_me()).username
    await callback_query.message.edit_text(
        "➕ **ADD ME TO YOUR GROUP**\n\n"
        "1. Add me to your group\n"
        f"   → [Click here to add](https://t.me/{bot_username}?startgroup=true)\n\n"
        "2. Make me admin (important!)\n\n"
        "3. Type /start in group\n\n"
        "4. Start playing with friends! 🏏"
    )
    await callback_query.answer()
