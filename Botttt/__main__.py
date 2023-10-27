from itertools import groupby
import importlib
from telegram import InputMediaPhoto
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters, ApplicationBuilder 
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent, InputMediaPhoto
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import InlineQueryHandler,CallbackQueryHandler, ChosenInlineResultHandler
from pymongo import MongoClient, ReturnDocument
import urllib.request
import random
from datetime import datetime, timedelta
from threading import Lock
import time

from Botttt.modules import ALL_MODULES
client = MongoClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
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

async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)

    # Get or create a lock for this chat
    if chat_id not in locks:
        locks[chat_id] = Lock()
    lock = locks[chat_id]

    # Use the lock to ensure that only one instance of this function can run at a time for this chat
    with lock:
        # Get message frequency and counter for this chat from the database
        chat_frequency = user_totals_collection.find_one({'chat_id': chat_id})
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
        user_totals_collection.update_one(
            {'chat_id': chat_id},
            {'$set': {'message_counter': message_counter}},
            upsert=True
        )

async def send_image(update: Update, context: CallbackContext) -> None:
    
    
    chat_id = update.effective_chat.id

    # Get all characters
    # Change it to this
    all_characters = list(collection.find({}))
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
    
async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if a character has been sent in this chat yet
    if chat_id not in last_characters:
        return

    # If someone has already guessed correctly
    if chat_id in first_correct_guesses:
        await update.message.reply_text(f'❌️ Already guessed by Someone..So Try Next Time Bruhh')
        return

    # Check if guess is correct
    guess = ' '.join(context.args).lower() if context.args else ''
    
    if guess and guess in last_characters[chat_id]['name'].lower():
        # Set the flag that someone has guessed correctly
        first_correct_guesses[chat_id] = user_id

        # Increment global count
        global_count = user_totals_collection.find_one_and_update(
            {'id': 'global'},
            {'$inc': {'count': 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        # Increment user's count in this group
        group_user = group_user_totals_collection.find_one({'group_id': chat_id, 'user_id': user_id})
        if group_user:
            # Update username and first_name if they have changed
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != group_user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != group_user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                group_user_totals_collection.update_one({'group_id': chat_id, 'user_id': user_id}, {'$set': update_fields})
            group_user_totals_collection.update_one({'group_id': chat_id, 'user_id': user_id}, {'$inc': {'total_count': 1}})
        elif hasattr(update.effective_user, 'username'):
            # Create new user document with total_count initialized to 1
            group_user_totals_collection.insert_one({
                'group_id': chat_id,
                'user_id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'total_count': 1  # Initialize total_count
            })

        # Add character to user's collection
        user = user_collection.find_one({'id': user_id})
        if user:
            # Update username and first_name if they have changed
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                user_collection.update_one({'id': user_id}, {'$set': update_fields})
            user_collection.update_one({'id': user_id}, {'$inc': {'total_count': 1}})
            
            # Add character to user's collection if not already present
            if not any(character['id'] == last_characters[chat_id]['id'] for character in user['characters']):
                user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
                
        elif hasattr(update.effective_user, 'username'):
            # Create new user document with total_count initialized to 1
            user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
                'total_count': 1  # Initialize total_count
            })

        await update.message.reply_text(f'Congooo ✅️! <a href="tg://user?id={user_id}">{update.effective_user.first_name}</a> guessed it right. The character is {last_characters[chat_id]["name"]} from {last_characters[chat_id]["anime"]}.', parse_mode='HTML')

    else:
        await update.message.reply_text('Incorrect guess. Try again.')


if __name__ == '__main__':
    application = ApplicationBuilder().token('6794007851:AAFOj7qlMXlyRU4GlNqjVtO-5snYvu6-cwc').build()
    
    
    COUNT= MessageHandler(filters.TEXT & ~filters.COMMAND, message_counter)
    application.add_handler(COUNT)
    COUTT= CommaHandler("guess", message_counter)
    application.add_handler(COUTT)
    
    application.run_polling()
