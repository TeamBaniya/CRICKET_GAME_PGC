# TODO: Add your code here
# MongoDB
MONGO_URI = "mongodb+srv://sparshshivare2606:sparshs2607@cluster0.cvditmt.mongodb.net/?appName=Cluster0"
DB_NAME = "cricket_bot"

# Bot Token (Yahan apna token dalna)
BOT_TOKEN = "8710613096:AAHOqrjfrKU-RNcVGKgHprD6ZW3nUhI-y4U"

# Admin IDs
ADMIN_IDS = [123456789]  # Apne admin IDs dalo

# Messages
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

• /start: Begin a solo match
• /joingame: Join an ongoing solo match
• /end_match: End the current game
• /feedback: Share your feedback
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

# Button Texts
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
}

# Callback Data
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
}

# Overs options
OVERS_OPTIONS = [1, 2, 3, 4, 5, 6, 7]
