from handlers.start import start_command, host_callback
from handlers.help import help_command, game_instructions_callback
from handlers.team import add_a_command, add_b_command, join_teama_command, join_teamb_command, members_list_command
from handlers.match import startgame_command
from handlers.gameplay import bowling_command, batting_command, swap_command, end_match_command
from handlers.auction import add_cap_command, rm_cap_command, cap_change_command, auction_id_command, start_auction_command, pause_auction_command, resume_auction_command, auction_host_change_command, xp_command, unhold_command, rm_auction_id_command
from handlers.callback import callback_handler

async def register_handlers(client, message):
    text = message.text.lower() if message.text else ""
    
    # Commands
    if text == "/start":
        await start_command(client, message)
    elif text == "/help":
        await help_command(client, message)
    elif text == "/startgame":
        await startgame_command(client, message)
    elif text == "/bowling":
        await bowling_command(client, message)
    elif text == "/batting":
        await batting_command(client, message)
    elif text == "/swap":
        await swap_command(client, message)
    elif text == "/end_match":
        await end_match_command(client, message)
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
    # Auction commands
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
    # Callback query
    elif message.callback_query:
        await callback_handler(client, message.callback_query)
