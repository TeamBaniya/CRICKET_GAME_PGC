# TODO: Add your code here
from handlers.start import start_handler
from handlers.help import help_handler
from handlers.team import team_add_handler, team_join_handler
from handlers.match import startgame_handler
from handlers.gameplay import bowling_handler, batting_handler
from handlers.auction import auction_handlers
from handlers.callback import callback_handler

async def register_handlers(client, message):
    text = message.text.lower() if message.text else ""
    
    if text.startswith("/start"):
        await start_handler(client, message)
    elif text.startswith("/help"):
        await help_handler(client, message)
    elif text.startswith("/startgame"):
        await startgame_handler(client, message)
    elif text.startswith("/bowling"):
        await bowling_handler(client, message)
    elif text.startswith("/batting"):
        await batting_handler(client, message)
    elif text.startswith(("/add_a", "/add_b", "/join_teama", "/join_teamb")):
        await team_add_handler(client, message)
    elif text.startswith(("/auction")):
        await auction_handlers(client, message)
    elif message.callback_query:
        await callback_handler(client, message.callback_query)
