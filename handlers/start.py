from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from config import IMAGE_URL, WELCOME_CAPTION, UPDATES_LINK, SUPPORT_LINK, PLAYZONE_LINK

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

    # 🔘 Buttons with Actions and Styles
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏏 PLAY ZONE", callback_data="play_zone", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("📊 LIVE SCORE", callback_data="live_score", style=ButtonStyle.DANGER)
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
    """Game instructions menu - jab PLAY ZONE dabaye"""
    from config import BUTTONS, CB
    
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
