from handlers.bowling import bowling_command, bowling_dm_handler
from handlers.batting import batting_command, handle_group_batting_number
from handlers.result import end_match
from handlers.game import create_game_command, joingame_command, start_timers
from handlers.start import start_command

async def register_handlers(client, message):
    # ========== GROUP MEIN NUMBER RECEIVE (BATTING) ==========
    if message.chat.type in ["group", "supergroup"] and message.text:
        text_stripped = message.text.strip()
        if text_stripped.isdigit() and 1 <= int(text_stripped) <= 6:
            await handle_group_batting_number(client, message)
            return
    
    # ========== DM ME NUMBER RECEIVE (BOWLING) ==========
    if message.chat.type == "private" and message.text:
        text_upper = message.text.upper()
        if text_upper in ["1", "2", "3", "4", "5", "6"]:
            await bowling_dm_handler(client, message)
            return
    
    text = message.text.lower() if message.text else ""
    
    # ========== COMMANDS ==========
    if text == "/start":
        await start_command(client, message)
    elif text == "/create_game":
        await create_game_command(client, message)
    elif text == "/joingame":
        await joingame_command(client, message)
    elif text == "/bowling":
        await bowling_command(client, message)
    elif text == "/batting":
        await batting_command(client, message)
    elif message.callback_query:
        from handlers.callback import callback_handler
        await callback_handler(client, message.callback_query)
