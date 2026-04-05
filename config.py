# TODO: Add your code here
import os
from dotenv import load_dotenv

load_dotenv()

# ========== MONGODB ==========
MONGO_URI = "mongodb+srv://sparshshivare2606:sparshs2607@cluster0.cvditmt.mongodb.net/?appName=Cluster0"
DB_NAME = "cricket_bot"

# ========== BOT TOKEN ==========
BOT_TOKEN = "8710613096:AAHOqrjfrKU-RNcVGKgHprD6ZW3nUhI-y4U"

# ========== ADMIN IDs ==========
ADMIN_IDS = [6572893382]  # Apne admin IDs dalo

# ========== LINKS (AAP YAHAN APNE LINKS DAALOGE) ==========
UPDATES_LINK = "https://t.me/your_updates_channel"      # 📢 UPDATES button
SUPPORT_LINK = "https://t.me/your_support_group"        # 🔗 SUPPORT button
PLAYZONE_LINK = "https://t.me/your_playzone_group"      # 🏏 PLAY ZONE button
LIVE_SCORE_LINK = "https://t.me/your_live_score_channel" # 📊 LIVE SCORE button

# ========== IMAGES/VIDEOS (AAP YAHAN APNE LINKS DAALOGE) ==========
IMAGE_URL = "https://files.catbox.moe/0odkk1.jpg"           # Welcome image
HOST_IMAGE_URL = "https://files.catbox.moe/0odkk1.jpg"     # Host selection image
BOWLING_VIDEO_URL = ""  # Bowling video link daalna (optional)
BATTING_VIDEO_URL = ""  # Batting video link daalna (optional)
SIX_VIDEO_URL = ""      # SIX! wala video link
FOUR_VIDEO_URL = ""     # FOUR! wala video link
WICKET_VIDEO_URL = ""   # WICKET! wala video link

# ========== GAME SETTINGS ==========
DEFAULT_OVERS = 2
MAX_OVERS = 7
BOWLING_TIMER_SECONDS = 60   # Bowler ke liye 60 seconds
JOINING_TIMER_SECONDS = 120  # Game join karne ke liye 2 minutes

# ========== BOWLING SPEED OPTIONS ==========
BOWLING_SPEEDS = ["FANCODE", "TANCODE", "ATHANSTAN", "FAST", "PHYSICAL", "63"]

# ========== BATTING RATINGS ==========
BATTING_RATINGS = {
    "ND BAT": 66,
    "MENTAL": 66,
    "PACE": 63,
    "PHYSICAL": 66
}

# ========== WELCOME CAPTION (for start.py) ==========
WELCOME_CAPTION = """
🏏 **𝐖ᴇʟᴄᴏᴍᴇ 𝐭ᴏ 𝐂ʀɪᴄᴋᴇᴛ 𝐁ᴏᴛ!**

🔴 **𝐋ɪᴠᴇ 𝐂ʀɪᴄᴋᴇᴛ 𝐒ᴄᴏʀᴇs:** Get real-time updates on live matches. Use /matches to see live scores.

🎮 **𝐌ᴀɴᴀɢᴇ 𝐘ᴏᴜʀ 𝐓ᴇᴀᴍ:** Strategize, set your lineup, and play the game just like a pro captain.

🗽 **1_VS_1:** Find one vs one match /1v1

Use /help to learn more about the game.
"""

# ========== MESSAGES ==========
WELCOME_MESSAGE = """
🏏 **CRICKET CHAMPIONSHIP** 🏏

**WELCOME TO CRICKET BOT!**

• **LIVE CRICKET SCORES:** Get real-time updates on live matches.
  Use /matches to see live scores.

• **MANAGE YOUR TEAM:** Strategize, set your lineup, and play the game just like a pro captain.

• **1_VS_1:** Find one vs one match /1v1

Use /help to learn more about the game.
"""

HELP_MESSAGE = """
Hello! 🎉 Need some help with Cricket Master Bot? Here are some tips to get you started:

- **Join a Match:** Ready to play? Start a new match or join an existing one with your friends. Just type /start in groups.

- **Manage Your Team:** Set up your lineup, choose your captain, and get ready to play. Use /startgame to get started.

- **Game Instructions:** New to the game? Type help to learn how to play and master the game.

- **Feedback:** We value your input! Share your /feedback with us in the support group.

- **Help and Support:** If you need assistance, visit our support group or type /help.

Enjoy your time with Cricket Master Bot! 🎉
"""

GAME_INSTRUCTIONS_MESSAGE = """
🎮 **GAME INSTRUCTIONS**

Choose your mode:
"""

SOLO_MODE_MESSAGE = """
🎯 **SOLO MODE**

• /solo_start: Begin a solo match
• /solo_stats: View your stats
• /solo_leaderboard: Top players
• /end_match: End the current game
"""

TEAM_MODE_MESSAGE = """
👥 **TEAM MODE COMMANDS**

**ADD MEMBERS:**
/add_A - add members to team A
/add_B - add members to team B

**REMOVE MEMBERS:**
/remove_A - remove members from team A
/remove_B - remove members from team B

**GAME PLAY:**
/startgame - to start the game
/bowling - choose the bowling person
/batting - choose the batting person
/swap - change playing position
/end_match - end the current game
"""

AUCTION_MESSAGE = """
💰 **AUCTION COMMANDS**

/add_cap - add auction captain
/rm_cap - remove auction captain
/cap_change_auction - change auction captain
/auction_id - send auction player ID
/start_auction - start auction
/pause_auction - pause auction
/resume_auction - resume auction
/auction_host_change - change auction host
/xp - put value on player
/unhold - unsold player list
/rm_auction_id - remove sold player
"""

HOST_MESSAGE = """
🎮 **New Game Alert!**

Who will be the game host for this match?
"""

TEAM_CREATION_MESSAGE = """
🏏 **Team Creation**

Team creation is underway!
Join Team A by sending /join_teamA
Join Team B by sending /join_teamB

Check members: /members_list
"""

OVERS_MESSAGE = """
🏏 **Cricket Game**

How many overs do you want for this game?
"""

MATCH_START_MESSAGE = """
🎉 OHOO! Let's play a {overs} overs Match!!

{bowling_team} will bowl first!

Now, choose your player!
"""

# ========== BOWLING MESSAGES ==========
BOWLING_START_MESSAGE = """
🎯 **Hey {bowler}, now you're bowling!**

Choose your bowling speed:
"""

BOWLING_NUMBER_MESSAGE = """
✅ **Speed {speed} selected!**

Now send number on bot PM (1-6 or W for wicket)
⏰ You have {seconds} seconds!
"""

BOWLING_WARNING_30 = """
⚠️ **Warning: {bowler}, you have 30 seconds left to send a number!**
"""

BOWLING_WARNING_10 = """
⚠️ **Warning: {bowler}, you have 10 seconds left to send a number!**
"""

BOWLING_TIMEOUT = """
⏰ **No message received from bowler, deducting 6 runs of bowler.**
❌ **Seems Bowling player is not responding, User Eliminated from the game !!**
"""

# ========== BATTING MESSAGES ==========
BATTING_START_MESSAGE = """
🏏 **Now Batter: {batter} can send number (1-6)!!**

📊 **Ratings:** ND BAT | MENTAL 66 | PACE 63 | PHYSICAL 66
"""

BATTING_WARNING_30 = """
⚠️ **Warning: {batter}, you have 30 seconds left to send a number!**
"""

BATTING_WARNING_10 = """
⚠️ **Warning: {batter}, you have 10 seconds left to send a number!**
"""

BATTING_TIMEOUT = """
⏰ **No message received from batter!**
"""

# ========== BALL RESULT MESSAGES ==========
BALL_RESULT_RUN = """
🏏 **{runs} RUN{'S' if runs > 1 else ''}!**

{run_type}
⏱️ {response_time}ms
"""

BALL_RESULT_SIX = """
🎯 **SIX!** 🚀

{run_type}
⏱️ {response_time}ms
"""

BALL_RESULT_FOUR = """
🎯 **FOUR!** 💥

{run_type}
⏱️ {response_time}ms
"""

BALL_RESULT_WICKET = """
🎯 **WICKET!** 🎯

{wicket_type}
⏱️ {response_time}ms
"""

# ========== PLAYER ROTATION ==========
NEW_BATSMAN_MESSAGE = """
🔄 **Number matches, {old_batter}**

👋 **Hey {new_batter}, now you're batter!**
🆕 **New batsman: {new_batter}**

🏀 **Get ready for the next ball!**
"""

NEW_BOWLER_MESSAGE = """
🔄 **Hey {new_bowler}, now you're bowling!**
"""

# ========== SOLO MODE MESSAGES ==========
SOLO_PLAYER_LIST_HEADER = """
🏏 **Cricket Game - PCG**
🎯 **SOLO PLAYERS**

"""

SOLO_PLAYER_FORMAT = """
{icon} **{name}** = {runs}({balls})
   • 4s: {fours}, 6s: {sixes}
   • ID: `{user_id}`
   • {ball_sequence}
"""

# ========== BUTTON TEXTS ==========
BUTTONS = {
    "I_AM_HOST": "🎮 I'm the Host",
    "PLAY_ZONE": "🏏 PLAY ZONE",
    "LIVE_SCORE": "📊 LIVE SCORE",
    "UPDATES": "📢 UPDATES",
    "SUPPORT": "🔗 SUPPORT",
    "ADD_TO_GROUP": "➕ ADD ME TO YOUR GROUP",
    "HELP": "❓ HELP",
    "GAME_INSTRUCTIONS": "🎮 Game Instructions",
    "DEVELOPER": "👨‍💻 DEVELOPER",
    "SOLO_PLAY": "🎯 Solo Play",
    "TEAM_PLAY": "👥 Team Play",
    "AUCTION": "💰 Auction",
    "HOME": "🏠 Home",
    "BACK": "◀️ BACK",
    "BOWLING": "🏏 /bowling",
    "BATTING": "🏏 /batting",
    "VOTE_GAME": "🗳️ VOTE GAME",
    "SOLO_TREE": "🌳 SOLO TREE COMMUNITY",
    "TIMING": "🎯 TIMING",
    "DIRECTION": "🎯 DIRECTION",
    "TAKE_RUN": "🏃 TAKE RUN",
}

# ========== CALLBACK DATA ==========
CB = {
    "HOST": "host",
    "SOLO": "solo",
    "TEAM": "team",
    "AUCTION": "auction",
    "HOME": "home",
    "BACK": "back",
    "BOWLING": "bowling",
    "BATTING": "batting",
    "HELP_MENU": "help_menu",
    "GAME_INSTRUCTIONS_MENU": "game_instructions",
    "ADD_TO_GROUP": "add_to_group",
    "UPDATES_LINK": "updates_link",
    "SUPPORT_LINK": "support_link",
    "DEVELOPER_INFO": "developer_info",
    "PLAY_ZONE": "play_zone",
    "LIVE_SCORE": "live_score",
    "UPDATES": "updates",
    "SUPPORT": "support",
    "VOTE_GAME": "vote_game",
    "SOLO_TREE": "solo_tree",
    "SOLO_PLAY": "solo_play",
    "TEAM_PLAY": "team_play",
    "TIMING": "timing",
    "DIRECTION": "direction",
    "TAKE_RUN": "take_run",
}

# ========== OVERS OPTIONS ==========
OVERS_OPTIONS = [1, 2, 3, 4, 5, 6, 7]

# ========== BOWLING SPEEDS LIST (for buttons) ==========
BOWLING_SPEEDS_BUTTONS = ["FANCODE", "TANCODE", "ATHANSTAN", "FAST", "PHYSICAL", "63"]

# ========== SOLO PLAYER ICONS ==========
SOLO_ICONS = ["🟢", "⚽", "🔥", "🌞", "💬", "🎮", "🏀", "🐍", "🕊️"]
