# TODO: Add your code here
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ButtonStyle
from handlers.join import create_game
import asyncio
from datetime import datetime, timedelta

# Active voting sessions
active_votes = {}

async def vote_game_command(client, message: Message):
    """Vote Game command - Start voting session"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if already active vote
    if chat_id in active_votes:
        await message.reply_text("⚠️ A voting session is already active!")
        return
    
    # Create voting session
    vote_data = {
        "host_id": user_id,
        "host_name": message.from_user.first_name,
        "start_time": datetime.now(),
        "end_time": datetime.now() + timedelta(minutes=2),
        "players": [user_id],
        "player_names": [message.from_user.first_name],
        "status": "voting",
        "message_id": None
    }
    active_votes[chat_id] = vote_data
    
    # Voting message with buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ JOIN GAME", callback_data="vote_join", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("❌ CANCEL", callback_data="vote_cancel", style=ButtonStyle.DANGER)
        ]
    ])
    
    msg = await message.reply_text(
        f"🗳️ **VOTING SESSION STARTED!**\n\n"
        f"👤 **Host:** {message.from_user.first_name}\n"
        f"⏰ **Time remaining:** 2 minutes\n\n"
        f"👥 **Players joined:** 1\n\n"
        f"Click **JOIN GAME** to participate!\n"
        f"Minimum 2 players needed to start.",
        reply_markup=buttons
    )
    
    vote_data["message_id"] = msg.id
    
    # Start timer
    asyncio.create_task(vote_timer(client, chat_id))


async def vote_timer(client, chat_id):
    """2 minute timer for voting"""
    for remaining in range(120, 0, -10):
        if chat_id not in active_votes:
            return
        
        vote_data = active_votes[chat_id]
        if vote_data["status"] != "voting":
            return
        
        players_count = len(vote_data["players"])
        minutes = remaining // 60
        seconds = remaining % 60
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ JOIN GAME", callback_data="vote_join", style=ButtonStyle.SUCCESS),
                InlineKeyboardButton("❌ CANCEL", callback_data="vote_cancel", style=ButtonStyle.DANGER)
            ]
        ])
        
        try:
            await client.edit_message_text(
                chat_id,
                vote_data["message_id"],
                f"🗳️ **VOTING SESSION ACTIVE!**\n\n"
                f"👤 **Host:** {vote_data['host_name']}\n"
                f"⏰ **Time remaining:** {minutes}:{seconds:02d}\n\n"
                f"👥 **Players joined:** {players_count}\n\n"
                f"Click **JOIN GAME** to participate!\n"
                f"Minimum 2 players needed.",
                reply_markup=buttons
            )
        except:
            pass
        
        await asyncio.sleep(10)
    
    # Time's up
    await end_vote_session(client, chat_id)


async def end_vote_session(client, chat_id):
    """End voting session and create game if enough players"""
    if chat_id not in active_votes:
        return
    
    vote_data = active_votes[chat_id]
    players_count = len(vote_data["players"])
    
    if players_count >= 2:
        # Create game
        await client.edit_message_text(
            chat_id,
            vote_data["message_id"],
            f"🎉 **GAME CREATED!** 🎉\n\n"
            f"👥 **Total players joined:** {players_count}\n\n"
            f"📝 **Players list:**\n" + "\n".join([f"  {i+1}. {name}" for i, name in enumerate(vote_data["player_names"])]) + "\n\n"
            f"🎮 **Join the game using** `/joingame`\n"
            f"⏰ You have 2 minutes to join!\n\n"
            f"Type `/startgame` when ready!"
        )
        
        # Create game in join system
        class FakeMessage:
            def __init__(self, chat, reply_text):
                self.chat = chat
                self.reply_text = reply_text
        
        fake_msg = FakeMessage(await client.get_chat(chat_id), None)
        await create_game(client, fake_msg, vote_data["host_id"])
        
    else:
        # Not enough players
        await client.edit_message_text(
            chat_id,
            vote_data["message_id"],
            f"⚠️ **Voting session expired due to inactivity.**\n\n"
            f"👥 **Players joined:** {players_count}/2 minimum\n\n"
            f"Start a new game with /vote_game"
        )
    
    del active_votes[chat_id]


async def vote_join_callback(callback_query: CallbackQuery):
    """Handle join game button click"""
    chat_id = callback_query.message.chat.id
    user = callback_query.from_user
    
    if chat_id not in active_votes:
        await callback_query.answer("❌ No active voting session!", show_alert=True)
        return
    
    vote_data = active_votes[chat_id]
    
    if vote_data["status"] != "voting":
        await callback_query.answer("❌ Voting session already ended!", show_alert=True)
        return
    
    if user.id in vote_data["players"]:
        await callback_query.answer("✅ You already joined!", show_alert=True)
        return
    
    # Add player
    vote_data["players"].append(user.id)
    vote_data["player_names"].append(user.first_name)
    
    await callback_query.answer(f"✅ {user.first_name} joined the game!", show_alert=True)
    
    # Update message
    players_count = len(vote_data["players"])
    time_left = (vote_data["end_time"] - datetime.now()).seconds
    minutes = time_left // 60
    seconds = time_left % 60
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ JOIN GAME", callback_data="vote_join", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("❌ CANCEL", callback_data="vote_cancel", style=ButtonStyle.DANGER)
        ]
    ])
    
    await callback_query.message.edit_text(
        f"🗳️ **VOTING SESSION ACTIVE!**\n\n"
        f"👤 **Host:** {vote_data['host_name']}\n"
        f"⏰ **Time remaining:** {minutes}:{seconds:02d}\n\n"
        f"👥 **Players joined:** {players_count}\n\n"
        f"Click **JOIN GAME** to participate!\n"
        f"Minimum 2 players needed.",
        reply_markup=buttons
    )


async def vote_cancel_callback(callback_query: CallbackQuery):
    """Handle cancel vote button click"""
    chat_id = callback_query.message.chat.id
    
    if chat_id in active_votes:
        del active_votes[chat_id]
    
    await callback_query.message.edit_text(
        "❌ **Voting session cancelled!**\n\n"
        "Start a new game with /vote_game"
    )
    await callback_query.answer()


async def vote_game_callback(callback_query: CallbackQuery):
    """Vote game callback from menu"""
    from handlers.start import start_command
    
    class FakeMessage:
        def __init__(self, chat, from_user, reply_text):
            self.chat = chat
            self.from_user = from_user
            self.reply_text = reply_text
    
    fake_msg = FakeMessage(
        callback_query.message.chat,
        callback_query.from_user,
        callback_query.message.reply_text
    )
    
    await vote_game_command(callback_query._client, fake_msg)
    await callback_query.answer()
