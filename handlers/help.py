# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from config import UPDATES_LINK, SUPPORT_LINK, OWNER_LINK

HELP_MESSAGE = """
Hello! 🤗 Need some help with Cricket Master Bot? Here are some tips to get you started:

🔹 **Join a Match:** Ready to play? Start a new match or join an existing one with your friends. Just type /start in groups.

🔹 **Manage Your Team:** Set up your lineup, choose your captain, and get ready to play. Use /startgame to get started.

🔹 **Game Instructions:** New to the game? Type help to learn how to play and master the game.

🔹 **Feedback:** We value your input! Share your /feedback with us in the support group.

🔹 **Help and Support:** If you need assistance, visit our support group or type /help.

👉 For a list of all available commands, click the "🎯 𝐆𝐚𝐦𝐞 𝐈𝐧𝐬𝐭𝐫𝐮𝐜𝐭𝐢𝐨𝐧𝐬" button below.

Enjoy your time with Cricket Master Bot! 🏏🚀
"""

GAME_INSTRUCTIONS_MESSAGE = """
🎮 **GAME INSTRUCTIONS**

Choose your mode to play:
"""

SOLO_MODE_MESSAGE = """
🏏 **Solo Mode:**

• /solo_start: Begin a solo match. Use the Solo button.
  - Next: Select your bowling mode by clicking Choose Random or Group Volunteer.

• /joingame: Join an ongoing solo match.

• /end_match: End the current game.

• /feedback: Share your feedback about the game and help us improve!

Ready to play? Let's see your skills on the field! 🌟
"""

TEAM_MODE_MESSAGE = """
👥 **Team Mode:**

• /startgame: Start a new team match

• /add_A @username - Add member to Team A
• /add_B @username - Add member to Team B

• /join_teamA - Join Team A
• /join_teamB - Join Team B

• /members_list - View team members

• /end_match - End the current game
"""

AUCTION_MESSAGE = """
💰 **Auction Mode:**

• /add_cap - Add auction captain
• /rm_cap - Remove auction captain
• /cap_change_auction - Change auction captain
• /auction_id - Send auction player ID
• /start_auction - Start auction
• /pause_auction - Pause auction
• /resume_auction - Resume auction
• /auction_host_change - Change auction host
• /xp - Put value on player
• /unhold - Unsold player list
• /rm_auction_id - Remove sold player
"""

async def help_command(client, message: Message):
    """Send help message with buttons"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ ADD ME TO GROUP", callback_data="add_to_group", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🎯 Game Instructions", callback_data="game_instructions", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("📢 UPDATES", url=UPDATES_LINK, style=ButtonStyle.DEFAULT),
            InlineKeyboardButton("🔗 SUPPORT", url=SUPPORT_LINK, style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("👨‍💻 DEVELOPER", url=OWNER_LINK, style=ButtonStyle.DEFAULT)
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
    """Solo mode specific menu - as per screenshot"""
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
        SOLO_MODE_MESSAGE,
        reply_markup=buttons
    )
    await callback_query.answer()


async def team_mode_menu(callback_query):
    """Team mode specific menu"""
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏏 Start Match", callback_data="start_match", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("📋 Rules", callback_data="team_rules", style=ButtonStyle.DEFAULT)
        ],
        [
            InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)
        ]
    ])
    await callback_query.message.edit_text(
        TEAM_MODE_MESSAGE,
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
        AUCTION_MESSAGE,
        reply_markup=buttons
    )
    await callback_query.answer()
