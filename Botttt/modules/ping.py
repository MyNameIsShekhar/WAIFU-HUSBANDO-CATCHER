import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from datetime import datetime, timedelta
import time
from Botttt import dispatcher, updater


def ping(update: Update, context: CallbackContext) -> None:
    start_time = time.time()
    message = update.message.reply_text('Pong!')
    end_time = time.time()
    elapsed_time = round((end_time - start_time) * 1000, 3)
    message.edit_text(f'Pong! {elapsed_time}ms')

PING_HANDLER = ("ping", ping, run_async=True)
dispatcher.add_handler(PING_HANDLER)

__command_list__ = ["ping"]

__handlers__ = [PING_HANDLER]
