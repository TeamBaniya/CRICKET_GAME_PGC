# TODO: Add your code here
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle

# Button configurations
BUTTONS_CONFIG = {
    # Main Menu
    "PLAY_ZONE": {"text": "🏏 PLAY ZONE", "style": ButtonStyle.PRIMARY, "callback": "play_zone"},
    "LIVE_SCORE": {"text": "📊 LIVE SCORE", "style": ButtonStyle.DEFAULT, "callback": "live_score"},
    "UPDATES": {"text": "📢 UPDATES", "style": ButtonStyle.DEFAULT, "callback": "updates"},
    "HELP": {"text": "❓ HELP", "style": ButtonStyle.DEFAULT, "callback": "help_menu"},
    "SUPPORT": {"text": "🔗 SUPPORT", "style": ButtonStyle.DEFAULT, "callback": "support"},
    "ADD_TO_GROUP": {"text": "➕ ADD ME TO YOUR GROUP", "style": ButtonStyle.SUCCESS, "callback": "add_to_group"},
    
    # Game Instructions
    "GAME_INSTRUCTIONS": {"text": "🎮 Game Instructions", "style": ButtonStyle.PRIMARY, "callback": "game_instructions"},
    "DEVELOPER": {"text": "👨‍💻 DEVELOPER", "style": ButtonStyle.DEFAULT, "callback": "developer"},
    "SOLO_PLAY": {"text": "🎯 Solo Play", "style": ButtonStyle.PRIMARY, "callback": "solo_mode"},
    "TEAM_PLAY": {"text": "👥 Team Play", "style": ButtonStyle.PRIMARY, "callback": "team_mode"},
    "AUCTION": {"text": "💰 Auction", "style": ButtonStyle.DANGER, "callback": "auction_mode"},
    "HOME": {"text": "🏠 Home", "style": ButtonStyle.DEFAULT, "callback": "home"},
    
    # Match related
    "I_AM_HOST": {"text": "🎮 I'm the Host", "style": ButtonStyle.PRIMARY, "callback": "host_selected"},
    "BOWLING": {"text": "🏏 /bowling", "style": ButtonStyle.PRIMARY, "callback": "bowling_select"},
    "BATTING": {"text": "🏏 /batting", "style": ButtonStyle.SUCCESS, "callback": "batting_select"},
    "BACK": {"text": "◀️ BACK", "style": ButtonStyle.DEFAULT, "callback": "back"},
    
    # Team management
    "JOIN_TEAM_A": {"text": "🔵 Join Team A", "style": ButtonStyle.PRIMARY, "callback": "join_team_a"},
    "JOIN_TEAM_B": {"text": "🔴 Join Team B", "style": ButtonStyle.DANGER, "callback": "join_team_b"},
    "MEMBERS_LIST": {"text": "📋 Members List", "style": ButtonStyle.DEFAULT, "callback": "members_list"},
    "START_GAME": {"text": "🎮 Start Game", "style": ButtonStyle.SUCCESS, "callback": "start_game"},
    
    # Auction
    "START_AUCTION": {"text": "🎉 Start Auction", "style": ButtonStyle.SUCCESS, "callback": "start_auction"},
    "PAUSE_AUCTION": {"text": "⏸️ Pause", "style": ButtonStyle.DEFAULT, "callback": "pause_auction"},
    "RESUME_AUCTION": {"text": "▶️ Resume", "style": ButtonStyle.PRIMARY, "callback": "resume_auction"},
}

def make_button(button_key: str, custom_callback: str = None):
    """Create a single button with style"""
    config = BUTTONS_CONFIG.get(button_key, {})
    return InlineKeyboardButton(
        text=config.get("text", button_key),
        callback_data=custom_callback or config.get("callback", button_key),
        style=config.get("style", ButtonStyle.DEFAULT)
    )

def make_row(*button_keys):
    """Create a row of buttons"""
    return [make_button(key) for key in button_keys]

def make_main_menu():
    """Main menu - 3 rows"""
    return InlineKeyboardMarkup([
        make_row("PLAY_ZONE", "LIVE_SCORE"),
        make_row("UPDATES", "HELP"),
        make_row("SUPPORT", "ADD_TO_GROUP"),
    ])

def make_help_menu():
    """Help menu buttons"""
    return InlineKeyboardMarkup([
        make_row("ADD_TO_GROUP", "GAME_INSTRUCTIONS"),
        make_row("UPDATES", "SUPPORT"),
        make_row("DEVELOPER"),
    ])

def make_game_instructions_menu():
    """Game instructions menu"""
    return InlineKeyboardMarkup([
        make_row("SOLO_PLAY", "TEAM_PLAY"),
        make_row("AUCTION", "HOME"),
    ])

def make_overs_menu():
    """Overs selection menu - 7 overs options"""
    overs_buttons = []
    row = []
    for i in range(1, 8):
        row.append(InlineKeyboardButton(
            text=f"{i} over{'s' if i > 1 else ''}",
            callback_data=f"overs_{i}",
            style=ButtonStyle.DEFAULT
        ))
        if len(row) == 3:
            overs_buttons.append(row)
            row = []
    if row:
        overs_buttons.append(row)
    
    overs_buttons.append([make_button("BACK")])
    return InlineKeyboardMarkup(overs_buttons)

def make_back_button():
    """Single back button"""
    return InlineKeyboardMarkup([make_row("BACK")])

def make_match_buttons():
    """Match gameplay buttons"""
    return InlineKeyboardMarkup([
        make_row("BOWLING", "BATTING"),
        make_row("BACK"),
    ])

def make_team_buttons():
    """Team creation buttons"""
    return InlineKeyboardMarkup([
        make_row("JOIN_TEAM_A", "JOIN_TEAM_B"),
        make_row("MEMBERS_LIST", "START_GAME"),
        make_row("BACK"),
    ])

def make_auction_buttons():
    """Auction control buttons"""
    return InlineKeyboardMarkup([
        make_row("START_AUCTION", "PAUSE_AUCTION", "RESUME_AUCTION"),
        make_row("BACK"),
    ])

def make_confirm_buttons():
    """Confirm/Cancel buttons"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel", style=ButtonStyle.DANGER)
        ]
    ])
