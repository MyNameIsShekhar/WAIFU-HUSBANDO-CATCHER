import importlib
from itertools import groupby

from motor.motor_asyncio import AsyncIOMotorClient 
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters, ApplicationBuilder 
from telegram.ext import InlineQueryHandler,CallbackQueryHandler, ChosenInlineResultHandler
from pymongo import MongoClient, ReturnDocument
import urllib.request
import random
from datetime import datetime, timedelta
from threading import Lock
import time


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

# Import asyncio
import asyncio

# Convert your function to async
async def get_next_sequence_number(sequence_name):
    # Get a handle to the sequence collection
    sequence_collection = db.sequences

    # Use find_one_and_update to atomically increment the sequence number
    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name}, 
        {'$inc': {'sequence_value': 1}}, 
        return_document=ReturnDocument.AFTER
    )

    # If this sequence doesn't exist yet, create it
    if not sequence_document:
        await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0

    return sequence_document['sequence_value']

async def upload(update: Update, context: CallbackContext) -> None:
    # Check if user is a sudo user
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = context.args
        if len(args) != 4:
            await update.message.reply_text('Incorrect format. Please use: /upload img_url Character-Name Anime-Name Rarity')
            return

        # Replace '-' with ' ' in character name and convert to title case
        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()

        # Check if image URL is valid
        try:
            urllib.request.urlopen(args[0])
        except:
            await update.message.reply_text('Invalid image URL.')
            return

        # Check if rarity is valid
        rarity_map = {1: "⚪ Common", 2: "🟣 Rare", 3: "🟡 Legendary", 4: "🟢 Medium"}
        try:
            rarity = rarity_map[int(args[3])]
        except KeyError:
            await update.message.reply_text('Invalid rarity. Please use 1, 2, 3, or 4.')
            return

        # Generate ID
        id = str(await get_next_sequence_number('character_id')).zfill(4)

        # Insert new character
        character = {
            'img_url': args[0],
            'name': character_name,
            'anime': anime,
            'rarity': rarity,
            'id': id
        }
        
        # Send message to channel
        message = await context.bot.send_photo(
            chat_id='-1001915956222',
            photo=args[0],
            caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n<b>Rarity:</b> {rarity}\n<b>ID:</b> {id}\nAdded by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
            parse_mode='HTML'
        )

        # Save message_id to character
        character['message_id'] = message.message_id
        await collection.insert_one(character)

        await update.message.reply_text('Successfully uploaded.')
    except Exception as e:
        await update.message.reply_text('Unsuccessfully uploaded.')
def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6656458442:AAGJ1nKC2qil9SMU3NbElluHSmHJrN8oZsg").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["upload", "lmao"], upload))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
