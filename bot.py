from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import logging
import requests 
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='1'),
         InlineKeyboardButton("Option 2", callback_data='2')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send an image from a URL
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://graph.org/file/60dcb0e5dc76ad24d52b8.jpg', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # Answer the query
    query.answer("You're not eligible." , show_alert=True)

def main() -> None:
    updater = Updater("6684851741:AAFdjonPh64ISqm0nBjS_xSI1fqCww6oBiw", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
