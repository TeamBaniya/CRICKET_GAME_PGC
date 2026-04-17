from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN
from handlers import register_handlers, callback_handler

# Bot application initialize
app = Application.builder().token(BOT_TOKEN).build()

# Message handler - commands aur messages ke liye
app.add_handler(MessageHandler(filters.ALL, register_handlers))

# Callback query handler - button presses ke liye
app.add_handler(CallbackQueryHandler(callback_handler))

# Bot run karo
if __name__ == "__main__":
    print("🤖 Cricket Game Bot is starting with PTB...")
    print("✅ Bot is now running!")
    app.run_polling()
