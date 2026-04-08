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

    # 🔘 Buttons - Sab direct links (ADD TO GROUP chhodkar)
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏏 PLAY ZONE", url=PLAYZONE_LINK, style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("📊 LIVE SCORE", url=LIVE_SCORE_LINK, style=ButtonStyle.DANGER)
        ],
        [
            InlineKeyboardButton("📢 UPDATES", url=UPDATES_LINK, style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("❓ HELP", callback_data="help_menu", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("🔗 SUPPORT", url=SUPPORT_LINK, style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("➕ ADD ME TO GROUP", callback_data="add_to_group", style=ButtonStyle.DANGER)
        ]
    ])

    # 🖼️ Image aur caption bhejna
    await message.reply_photo(
        photo=IMAGE_URL,
        caption=WELCOME_CAPTION,
        reply_markup=buttons
    )


async def game_instructions_menu(callback_query):
    """Game instructions menu - jab HELP ke andar se aayega"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Solo Play", callback_data="solo_play", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("👥 Team Play", callback_data="team_play", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("💰 Auction", callback_data="auction", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🗳️ VOTE GAME", callback_data="vote_game", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🌳 SOLO TREE COMMUNITY", callback_data="solo_tree", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("◀️ BACK", callback_data="back", style=ButtonStyle.DEFAULT)
        ]
    ])
    
    await callback_query.message.edit_text(
        "🎮 **GAME INSTRUCTIONS**\n\nChoose your mode:",
        reply_markup=buttons
    )
    await callback_query.answer()


async def host_callback(callback_query):
    """Callback for 'I'm the Host' button"""
    user = callback_query.from_user
    username = user.first_name or user.username or "User"
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🗳️ VOTE GAME", callback_data="vote_game", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🌳 SOLO TREE COMMUNITY", callback_data="solo_tree", style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("◀️ BACK", callback_data="back_to_main", style=ButtonStyle.DEFAULT)
        ]
    ])
    
    await callback_query.message.edit_text(
        f"🎮 **{username} is now the game host!**\n\n"
        f"Game host can create teams now.\n\n"
        f"Let's get the match started! 🏏",
        reply_markup=buttons
    )
    await callback_query.answer()


async def solo_tree_callback(callback_query):
    """Solo tree community callback"""
    from handlers.solo import solo_tree_community
    await solo_tree_community(callback_query)


async def help_menu_callback(callback_query):
    """Help menu button callback"""
    from handlers.help import help_command
    
    class FakeMessage:
        def __init__(self, chat, from_user, edit_text):
            self.chat = chat
            self.from_user = from_user
            self.reply_text = edit_text
    
    fake_msg = FakeMessage(
        callback_query.message.chat,
        callback_query.from_user,
        callback_query.message.edit_text
    )
    await help_command(callback_query._client, fake_msg)
    await callback_query.answer()


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


async def back_to_main_callback(callback_query):
    """Back to main menu"""
    await start_command(callback_query._client, callback_query.message)
    await callback_query.answer()
