from handlers.start import start_command, add_to_group_callback
from handlers.help import help_command
from handlers.team import add_a_command, add_b_command, join_teama_command, join_teamb_command, members_list_command
from handlers.match import startgame_command
from handlers.gameplay import bowling_command, swap_command, end_match_command, handle_group_batting_number
from handlers.auction import add_cap_command, rm_cap_command, cap_change_command, auction_id_command, start_auction_command, pause_auction_command, resume_auction_command, auction_host_change_command, xp_command, unhold_command, rm_auction_id_command
from handlers.join import joingame_command
from handlers.dm_handler import handle_dm_message
from handlers.game import create_game_command

async def register_handlers(client, message):
    # ✅ PUBLIC BOT - Sabko access hai
    
    # ========== GROUP MEIN NUMBER RECEIVE KARNA (BATTING) ==========
    if message.chat.type in ["group", "supergroup"] and message.text:
        text_stripped = message.text.strip()
        if text_stripped.isdigit() and 1 <= int(text_stripped) <= 6:
            # User ne 1-6 number bheja - check if he is current batsman
            await handle_group_batting_number(client, message)
            return
    
    # ========== DM ME NUMBER RECEIVE KARNA (BOWLING) ==========
    if message.chat.type == "private" and message.text:
        text_upper = message.text.upper()
        if text_upper in ["1", "2", "3", "4", "5", "6"]:
            await handle_dm_message(client, message)
            return
    
    text = message.text.lower() if message.text else ""
    
    # ========== COMMANDS ==========
    
    # General Commands
    if text == "/start":
        await start_command(client, message)
    elif text == "/help":
        await help_command(client, message)
    elif text == "/create_game":
        await create_game_command(client, message)
    
    # Game Commands
    elif text == "/startgame":
        await startgame_command(client, message)
    elif text == "/bowling":
        await bowling_command(client, message)
    elif text == "/swap":
        await swap_command(client, message)
    elif text == "/end_match":
        await end_match_command(client, message)
    elif text == "/joingame":
        await joingame_command(client, message)
    
    # Team Commands
    elif text.startswith("/add_a"):
        await add_a_command(client, message)
    elif text.startswith("/add_b"):
        await add_b_command(client, message)
    elif text.startswith("/join_teama"):
        await join_teama_command(client, message)
    elif text.startswith("/join_teamb"):
        await join_teamb_command(client, message)
    elif text == "/members_list":
        await members_list_command(client, message)
    
    # Auction Commands
    elif text == "/add_cap":
        await add_cap_command(client, message)
    elif text == "/rm_cap":
        await rm_cap_command(client, message)
    elif text == "/cap_change_auction":
        await cap_change_command(client, message)
    elif text == "/auction_id":
        await auction_id_command(client, message)
    elif text == "/start_auction":
        await start_auction_command(client, message)
    elif text == "/pause_auction":
        await pause_auction_command(client, message)
    elif text == "/resume_auction":
        await resume_auction_command(client, message)
    elif text == "/auction_host_change":
        await auction_host_change_command(client, message)
    elif text == "/xp":
        await xp_command(client, message)
    elif text == "/unhold":
        await unhold_command(client, message)
    elif text == "/rm_auction_id":
        await rm_auction_id_command(client, message)
    
    # ========== CALLBACK QUERIES ARE HANDLED IN main.py ==========
    # @bot.on_callback_query() handles button clicks
