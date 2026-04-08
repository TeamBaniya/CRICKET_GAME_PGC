# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from database import db
from datetime import datetime

# Store team data for active games
team_data = {}

TEAM_MODE_MESSAGE = """
👥 **TEAM MODE COMMANDS**

🌟 𝐌ᴇᴍʙᴇʀs 𝐀ᴅᴅɪɴɢ:

/add_A - add members to team A  
/add_B - add members to team B  

Eg: /add_A 1  or /add_A @username  
(Use the player number of your team)

🌟 𝐌ᴇᴍʙᴇʀs 𝐑ᴇᴍᴏᴠɪɴɢ:

/remove_A - remove members from team A  
/remove_B - remove members from team B  

Eg: /remove_A 2  
(Use the player number of your team)

🌟 𝐆ᴀᴍᴇ 𝐏ʟᴀʏ 𝐂ᴏᴍᴍᴀɴᴅs:

/startgame - to start the game  

/bowling - choose the bowling person of team A or B  
Eg: /bowling 3  
(Use the team A or B player number for bowling)

/batting - choose the batting person of team A or B  
Eg: /batting 4  
(Use the team A or B player number for batting)

/swap - to change the playing position of the current team  

/end_match - to end the current game  

/Feedback - give your feedback about the game
"""


async def add_a_command(client, message: Message):
    """Add member to Team A"""
    chat_id = message.chat.id
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text("❌ Usage: /add_A @username or /add_A 1\n\nExample: /add_A @player_name")
        return
    
    # Initialize team data if not exists
    if chat_id not in team_data:
        team_data[chat_id] = {
            "team_a": [],
            "team_b": [],
            "created_at": datetime.now()
        }
    
    player_name = args[1]
    player_number = len(team_data[chat_id]["team_a"]) + 1
    
    team_data[chat_id]["team_a"].append({
        "number": player_number,
        "name": player_name,
        "added_by": message.from_user.id
    })
    
    await message.reply_text(
        f"✅ **Player {player_name} added to Team A!** (Player #{player_number})\n\n"
        f"📊 Team A size: {len(team_data[chat_id]['team_a'])} players\n"
        f"📊 Team B size: {len(team_data[chat_id]['team_b'])} players"
    )


async def add_b_command(client, message: Message):
    """Add member to Team B"""
    chat_id = message.chat.id
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text("❌ Usage: /add_B @username or /add_B 1\n\nExample: /add_B @player_name")
        return
    
    # Initialize team data if not exists
    if chat_id not in team_data:
        team_data[chat_id] = {
            "team_a": [],
            "team_b": [],
            "created_at": datetime.now()
        }
    
    player_name = args[1]
    player_number = len(team_data[chat_id]["team_b"]) + 1
    
    team_data[chat_id]["team_b"].append({
        "number": player_number,
        "name": player_name,
        "added_by": message.from_user.id
    })
    
    await message.reply_text(
        f"✅ **Player {player_name} added to Team B!** (Player #{player_number})\n\n"
        f"📊 Team A size: {len(team_data[chat_id]['team_a'])} players\n"
        f"📊 Team B size: {len(team_data[chat_id]['team_b'])} players"
    )


async def remove_a_command(client, message: Message):
    """Remove member from Team A"""
    chat_id = message.chat.id
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text("❌ Usage: /remove_A <player_number>\n\nExample: /remove_A 2")
        return
    
    if chat_id not in team_data:
        await message.reply_text("❌ No active team game found! Start with /startgame first.")
        return
    
    try:
        player_number = int(args[1])
        team_a = team_data[chat_id]["team_a"]
        
        # Find and remove player
        for i, player in enumerate(team_a):
            if player["number"] == player_number:
                removed = team_a.pop(i)
                await message.reply_text(f"❌ Player {removed['name']} removed from Team A!")
                return
        
        await message.reply_text(f"❌ Player #{player_number} not found in Team A!")
    except ValueError:
        await message.reply_text("❌ Please enter a valid player number!")


async def remove_b_command(client, message: Message):
    """Remove member from Team B"""
    chat_id = message.chat.id
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text("❌ Usage: /remove_B <player_number>\n\nExample: /remove_B 2")
        return
    
    if chat_id not in team_data:
        await message.reply_text("❌ No active team game found! Start with /startgame first.")
        return
    
    try:
        player_number = int(args[1])
        team_b = team_data[chat_id]["team_b"]
        
        # Find and remove player
        for i, player in enumerate(team_b):
            if player["number"] == player_number:
                removed = team_b.pop(i)
                await message.reply_text(f"❌ Player {removed['name']} removed from Team B!")
                return
        
        await message.reply_text(f"❌ Player #{player_number} not found in Team B!")
    except ValueError:
        await message.reply_text("❌ Please enter a valid player number!")


async def join_teama_command(client, message: Message):
    """User join Team A command"""
    chat_id = message.chat.id
    user = message.from_user
    
    if chat_id not in team_data:
        team_data[chat_id] = {
            "team_a": [],
            "team_b": [],
            "created_at": datetime.now()
        }
    
    # Check if user already in team
    for player in team_data[chat_id]["team_a"]:
        if player.get("user_id") == user.id:
            await message.reply_text("❌ You are already in Team A!")
            return
    
    for player in team_data[chat_id]["team_b"]:
        if player.get("user_id") == user.id:
            await message.reply_text("❌ You are already in Team B! Leave that team first.")
            return
    
    player_number = len(team_data[chat_id]["team_a"]) + 1
    
    team_data[chat_id]["team_a"].append({
        "number": player_number,
        "name": f"@{user.username}" if user.username else user.first_name,
        "user_id": user.id,
        "first_name": user.first_name
    })
    
    await message.reply_text(
        f"✅ **{user.first_name} joined Team A!** (Player #{player_number})\n\n"
        f"📊 Team A: {len(team_data[chat_id]['team_a'])} players\n"
        f"📊 Team B: {len(team_data[chat_id]['team_b'])} players"
    )


async def join_teamb_command(client, message: Message):
    """User join Team B command"""
    chat_id = message.chat.id
    user = message.from_user
    
    if chat_id not in team_data:
        team_data[chat_id] = {
            "team_a": [],
            "team_b": [],
            "created_at": datetime.now()
        }
    
    # Check if user already in team
    for player in team_data[chat_id]["team_b"]:
        if player.get("user_id") == user.id:
            await message.reply_text("❌ You are already in Team B!")
            return
    
    for player in team_data[chat_id]["team_a"]:
        if player.get("user_id") == user.id:
            await message.reply_text("❌ You are already in Team A! Leave that team first.")
            return
    
    player_number = len(team_data[chat_id]["team_b"]) + 1
    
    team_data[chat_id]["team_b"].append({
        "number": player_number,
        "name": f"@{user.username}" if user.username else user.first_name,
        "user_id": user.id,
        "first_name": user.first_name
    })
    
    await message.reply_text(
        f"✅ **{user.first_name} joined Team B!** (Player #{player_number})\n\n"
        f"📊 Team A: {len(team_data[chat_id]['team_a'])} players\n"
        f"📊 Team B: {len(team_data[chat_id]['team_b'])} players"
    )


async def members_list_command(client, message: Message):
    """Show current team members"""
    chat_id = message.chat.id
    
    if chat_id not in team_data or (not team_data[chat_id]["team_a"] and not team_data[chat_id]["team_b"]):
        await message.reply_text("📋 **No players added yet!**\n\nUse /add_A or /add_B to add players.")
        return
    
    # Format Team A list
    team_a_list = "\n".join([f"  {p['number']}. {p['name']}" for p in team_data[chat_id]["team_a"]])
    team_a_text = team_a_list if team_a_list else "  No players yet"
    
    # Format Team B list
    team_b_list = "\n".join([f"  {p['number']}. {p['name']}" for p in team_data[chat_id]["team_b"]])
    team_b_text = team_b_list if team_b_list else "  No players yet"
    
    await message.reply_text(
        f"📋 **CURRENT TEAM MEMBERS**\n\n"
        f"🔵 **TEAM A** ({len(team_data[chat_id]['team_a'])} players)\n{team_a_text}\n\n"
        f"🔴 **TEAM B** ({len(team_data[chat_id]['team_b'])} players)\n{team_b_text}\n\n"
        f"Type /startgame to begin the match!"
    )


async def clear_teams(chat_id):
    """Clear all teams for a chat"""
    if chat_id in team_data:
        del team_data[chat_id]
    return True


async def get_teams(chat_id):
    """Get team data for a chat"""
    if chat_id in team_data:
        return team_data[chat_id]
    return None


async def team_mode_menu(callback_query):
    """Team mode menu with back button"""
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ BACK", callback_data="back_to_instructions", style=ButtonStyle.DEFAULT)]
    ])
    await callback_query.message.edit_text(TEAM_MODE_MESSAGE, reply_markup=buttons)
    await callback_query.answer()
