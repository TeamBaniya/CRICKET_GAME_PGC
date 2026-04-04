# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from config import UPDATES_LINK, SUPPORT_LINK

HELP_MESSAGE = """
Hello! 🎉 Need some help with Cricket Master Bot?

• **Join a Match:** Type /start in groups
• **Manage Your Team:** Use /startgame to get started
• **Game Instructions:** Click below button
• **Feedback:** Share your /feedback

Enjoy your time with Cricket Master Bot! 🎉
"""

GAME_INSTRUCTIONS_MESSAGE = """
🎮 **GAME INSTRUCTIONS**

Choose your mode to play:
"""

async def help_command(client, message: Message):
    """Send help message with buttons"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ ADD ME TO GROUP", callback_data="add_to_group", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🎮 Game Instructions", callback_data="game_instructions", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("📢 UPDATES", url=UPDATES_LINK, style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("🔗 SUPPORT", url=SUPPORT_LINK, style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("👨‍💻 DEVELOPER", callback_data="developer", style=ButtonStyle.DEFAULT)
        ]
    ])
    await message.reply_text(HELP_MESSAGE, reply_markup=buttons)


async def game_instructions_menu(callback_query):
    """Game instructions menu with all game modes"""
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
            InlineKeyboardButton("🏠 Home", callback_data="home", style=ButtonStyle.DEFAULT)
        ]
    ])
    await callback_query.message.edit_text(
        GAME_INSTRUCTIONS_MESSAGE,
        reply_markup=buttons
    )
    await callback_query.answer()


async def solo_mode_menu(callback_query):
    """Solo mode specific menu"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎮 Start Solo Match", callback_data="solo_start", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("📊 My Stats", callback_data="solo_stats", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="solo_leaderboard", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)
        ]
    ])
    await callback_query.message.edit_text(
        "🎯 **SOLO MODE**\n\n"
        "Play cricket matches against the bot!\n\n"
        "• /solo_start - Start a new match\n"
        "• /solo_stats - View your statistics\n"
        "• /solo_leaderboard - Top players list\n\n"
        "Send numbers 1-6 to play your shots!",
        reply_markup=buttons
    )
    await callback_query.answer()


async def team_mode_menu(callback_query):
    """Team mode specific menu"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Create Team", callback_data="create_team", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🏏 Start Match", callback_data="start_match", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("📋 Rules", callback_data="team_rules", style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)
        ]
    ])
    await callback_query.message.edit_text(
        "👥 **TEAM MODE**\n\n"
        "Play with friends!\n\n"
        "**Commands:**\n"
        "• /add_A @username - Add to Team A\n"
        "• /add_B @username - Add to Team B\n"
        "• /startgame - Start the match\n"
        "• /members_list - View team members\n\n"
        "Team with most runs wins!",
        reply_markup=buttons
    )
    await callback_query.answer()


async def auction_menu(callback_query):
    """Auction mode specific menu"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 Start Auction", callback_data="start_auction", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("📋 Rules", callback_data="auction_rules", style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)
        ]
    ])
    await callback_query.message.edit_text(
        "💰 **AUCTION MODE**\n\n"
        "Buy and sell players!\n\n"
        "**Commands:**\n"
        "• /add_cap - Add auction captain\n"
        "• /start_auction - Start auction\n"
        "• /auction_id <id> - Put player for auction\n"
        "• /xp <amount> - Place your bid\n"
        "• /unhold - View unsold players\n\n"
        "Get your dream team!",
        reply_markup=buttons
    )
    await callback_query.answer()
