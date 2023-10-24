import importlib
from itertools import groupby
from telegram import InputMediaPhoto
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters, ApplicationBuilder 
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent, InputMediaPhoto
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import InlineQueryHandler,CallbackQueryHandler, ChosenInlineResultHandler
from motor.motor_asyncio import AsyncIOMotorClient

import urllib.request
import random
from datetime import datetime, timedelta
from threading import Lock
import time


from Botttt.modules import ALL_MODULES
client = AsyncIOMotorClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
db = client['Waifus_lol']
collection = db['anime_characters_lol']

# Get the collection for user totals
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]

group_user_totals_collection = db['group_user_totalssssss']


# List of sudo users
sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651', '5813998595', '5813403535', '6393627898', '5952787198', '6614280216','6248411931','5216262234','1608353423']


# Create a dictionary of locks
locks = {}
# Counter for messages in each group
message_counters = {}
spam_counters = {}
# Last sent character in each group
last_characters = {}

# Characters that have been sent in each group
sent_characters = {}

# Keep track of the user who guessed correctly first in each group
first_correct_guesses = {}

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("Botttt.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module






async def change_time(update: Update, context: CallbackContext) -> None:
    # Check if user is a group admin
    user = update.effective_user
    chat = update.effective_chat

    if chat.get_member(user.id) not in ChatMember.ADMINISTRATOR:
        await update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = context.args
        if len(args) != 1:
            await update.message.reply_text('Incorrect format. Please use: /changetime NUMBER')
            return

        # Check if the provided number is greater than or equal to 100
        new_frequency = int(args[0])
        if new_frequency < 100:
            await update.message.reply_text('The message frequency must be greater than or equal to 100.')
            return

        # Change message frequency for this chat in the database
        chat_frequency = await user_totals_collection.find_one_and_update(
            {'chat_id': str(chat.id)},
            {'$set': {'message_frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        await update.message.reply_text(f'Successfully changed character appearance frequency to every {new_frequency} messages.')
    except Exception as e:
        await update.message.reply_text('Failed to change character appearance frequency.')



async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)

    # Get or create a lock for this chat
    if chat_id not in locks:
        locks[chat_id] = Lock()
    lock = locks[chat_id]

    # Use the lock to ensure that only one instance of this function can run at a time for this chat
    with lock:
        # Get message frequency and counter for this chat from the database
        chat_frequency =  await user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = await chat_frequency.get('message_frequency', 10)
            message_counter = await chat_frequency.get('message_counter', 0)
        else:
            # Default to 20 messages if not set
            message_frequency =10
            message_counter = 0

        # Increment counter for this chat
        message_counter += 1

        # Send image after every message_frequency messages
        if message_counter % message_frequency == 0:
            await send_image(update, context)
            # Reset counter for this chat
            message_counter = 0

        # Update counter in the database
        await user_totals_collection.update_one(
            {'chat_id': chat_id},
            {'$set': {'message_counter': message_counter}},
            upsert=True
        )



async def send_image(update: Update, context: CallbackContext) -> None:
    
    
    chat_id = update.effective_chat.id

    # Get all characters
    # Change it to this
    all_characters = await list(collection.find({}))
    # Initialize sent characters list for this chat if it doesn't exist
    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    # Reset sent characters list if all characters have been sent
    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    # Select a random character that hasn't been sent yet
    character = await random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])

    # Add character to sent characters list and set as last sent character
    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    # Reset first correct guess when a new character is sent
    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    # Send image with caption
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption="Use /Guess Command And.. Guess This Character Name.."
            )
    








if __name__ == '__main__':
    application = ApplicationBuilder().token('6794007851:AAFOj7qlMXlyRU4GlNqjVtO-5snYvu6-cwc').build()
    
    CHANGETIME = CommandHandler('changetime', change_time)
    application.add_handler(CHANGETIME)
    COUNT= MessageHandler(filters.TEXT & ~filters.COMMAND, message_counter)
    application.add_handler(COUNT)
    
    application.run_polling()
