import importlib
from telegram import InputMediaPhoto
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent, InputMediaPhoto
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

from itertools import groupby
from telegram import Update
from motor.motor_asyncio import AsyncIOMotorClient 
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters, Application
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
async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)

    # Get or create a lock for this chat
    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    # Use the lock to ensure that only one instance of this function can run at a time for this chat
    async with lock:
        # Get message frequency and counter for this chat from the database
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get('message_frequency', 10)
            message_counter = chat_frequency.get('message_counter', 0)
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
# Import asyncio


# Convert your function to async
async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    # Get all characters
    all_characters = list(await collection.find({}).to_list(length=None))
    
    # Initialize sent characters list for this chat if it doesn't exist
    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    # Reset sent characters list if all characters have been sent
    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    # Select a random character that hasn't been sent yet
    character = random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])

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
        caption="""***A New Character Has Just Appeared Use /guess [name]!👒
And Add This Character In You Collection***""",
        parse_mode='Markdown')
    
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
        global_count = await user_totals_collection.find_one_and_update(
            {'id': 'global'},
            {'$inc': {'count': 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        # Increment user's count in this group
        group_user = await group_user_totals_collection.find_one({'group_id': chat_id, 'user_id': user_id})
        if group_user:
            # Update username and first_name if they have changed
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != group_user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != group_user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await group_user_totals_collection.update_one({'group_id': chat_id, 'user_id': user_id}, {'$set': update_fields})
            await group_user_totals_collection.update_one({'group_id': chat_id, 'user_id': user_id}, {'$inc': {'total_count': 1}})
        elif hasattr(update.effective_user, 'username'):
            # Create new user document with total_count initialized to 1
            await group_user_totals_collection.insert_one({
                'group_id': chat_id,
                'user_id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'total_count': 1  # Initialize total_count
            })

        # Add character to user's collection
        user = await user_collection.find_one({'id': user_id})
        if user:
            # Update username and first_name if they have changed
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await user_collection.update_one({'id': user_id}, {'$set': update_fields})
            await user_collection.update_one({'id': user_id}, {'$inc': {'total_count': 1}})
            
            # Add character to user's collection if not already present
            if not any(character['id'] == last_characters[chat_id]['id'] for character in user['characters']):
                await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
                
        elif hasattr(update.effective_user, 'username'):
            # Create new user document with total_count initialized to 1
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
                'total_count': 1  # Initialize total_count
            })
        await update.message.reply_text(f'Congooo ✅️! <a href="tg://user?id={user_id}">{update.effective_user.first_name}</a> guessed it right. The character is {last_characters[chat_id]["name"]} from {last_characters[chat_id]["anime"]}.', parse_mode='HTML')

    else:
        await update.message.reply_text('Incorrect guess. Try again.')

async def change_time(update: Update, context: CallbackContext) -> None:
    # Check if user is a group admin
    user = update.effective_user
    chat = update.effective_chat
    member = await chat.get_member(user.id)

    if member.status not in ('administrator', 'creator'):
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
        
async def group_leaderboard(update: Update, context: CallbackContext) -> None:
    # Get the chat ID
    chat_id = update.effective_chat.id

    # Create inline keyboard
    keyboard = [
        [InlineKeyboardButton('My Group Rank', callback_data='group_leaderboard_myrank')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get group leaderboard data
    cursor = group_user_totals_collection.find({'group_id': chat_id}).sort('total_count', -1).limit(10)
    leaderboard_data = await cursor.to_list(length=10)

    # Start of the leaderboard message
    leaderboard_message = "***TOP 10 MOST GUESSED USERS IN THIS GROUP***\n\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username', 'Unknown')
        first_name = user.get('first_name', 'Unknown')
        if len(first_name) > 7:
            first_name = first_name[:7] + '...'
        count = user['total_count']
        leaderboard_message += f'{i} [{first_name}](https://t.me/{username})- {count}\n'

    # Choose a random photo URL
    photo_urls = [
        "https://graph.org/file/38767e79402baa8b04125.jpg",
        "https://graph.org/file/9bbee80d02c720004ab8d.jpg",
        "https://graph.org/file/cd0d8ca9bcfe489a23f82.jpg",
        "https://graph.org//file/e65e9605f3beb5c76026b.jpg",
        "https://graph.org//file/88c0fc2309930c591d98b.jpg"
    ]
    photo_url = random.choice(photo_urls)

    # Send photo with caption
    await update.message.reply_photo(photo=photo_url, caption=leaderboard_message, reply_markup=reply_markup, parse_mode='Markdown')
    
async def group_leaderboard_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # Get user's total count in this group
    user_total = await group_user_totals_collection.find_one({'group_id': query.message.chat.id, 'user_id': query.from_user.id})
    
    if user_total is None:
        await query.answer('You are not in this rank.', show_alert=True)
        return

    user_total_count = user_total['total_count']

    # Get sorted list of total counts in this group
    cursor = group_user_totals_collection.find({'group_id': query.message.chat.id}, {'total_count': 1, '_id': 0})
    sorted_counts = sorted(await cursor.to_list(length=100), key=lambda x: x['total_count'], reverse=True)

    # Get user's rank
    user_rank = sorted_counts.index({'total_count': user_total_count}) + 1

    await query.answer(f'Your rank in this group is {user_rank}.', show_alert=True)

async def leaderboard(update: Update, context: CallbackContext) -> None:
    # Create inline keyboard
    keyboard = [
        [InlineKeyboardButton('My Rank', callback_data='leaderboard_myrank')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get global leaderboard data
    cursor = user_collection.find().sort('total_count', -1).limit(10)
    leaderboard_data = await cursor.to_list(length=10)

    # Start of the leaderboard message
    leaderboard_message = "***TOP 10 MOST GUESSED USERS***\n\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username', 'Unknown')
        first_name = user.get('first_name', 'Unknown')
        if len(first_name) > 7:
            first_name = first_name[:10] + '...'
        count = user['total_count']
        leaderboard_message += f'{i}. [{first_name}](https://t.me/{username})- {count}\n'

    # Choose a random photo URL
    photo_urls = [
        "https://graph.org/file/38767e79402baa8b04125.jpg",
        "https://graph.org/file/9bbee80d02c720004ab8d.jpg",
        "https://graph.org/file/cd0d8ca9bcfe489a23f82.jpg",
        "https://graph.org//file/e65e9605f3beb5c76026b.jpg",
        "https://graph.org//file/88c0fc2309930c591d98b.jpg"
    ]
    photo_url = random.choice(photo_urls)

    # Send photo with caption
    await update.message.reply_photo(photo=photo_url, caption=leaderboard_message, reply_markup=reply_markup, parse_mode='Markdown')


async def leaderboard_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # Get user's total count
    user_total = await user_collection.find_one({'id': query.from_user.id})
    
    if user_total is None:
        await query.answer('You are not in this rank.', show_alert=True)
        return

    user_total_count = user_total['total_count']

    # Get sorted list of total counts
    cursor = user_collection.find({}, {'total_count': 1, '_id': 0})
    sorted_counts = sorted(await cursor.to_list(length=100), key=lambda x: x['total_count'], reverse=True)

    # Get user's rank
    user_rank = sorted_counts.index({'total_count': user_total_count}) + 1

    await query.answer(f'Your rank is {user_rank}.', show_alert=True)
async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    if query.isdigit():
        user = await user_collection.find_one({'id': int(query)})

        if user:
            # Get the next batch of characters
            characters = user['characters'][offset:offset+50]

            # Check if there are more characters
            if len(characters) > 50:
                # If so, remove the extra character and set the next offset
                characters = characters[:50]
                next_offset = str(offset + 50)
            else:
                # If not, set next_offset to None to indicate no more results
                next_offset = None

            results = []
            added_characters = set()
            for character in characters:
                if character['name'] not in added_characters:
                    anime_characters_guessed = sum(c['anime'] == character['anime'] for c in user['characters'])
                    total_anime_characters = await collection.count_documents({'anime': character['anime']})

                    # Get the character's rarity
                    rarity = character.get('rarity', "Don't have rarity.. Coz u Guessed before implement rarity.. in this bot")

                    results.append(
                        InlineQueryResultPhoto(
                            thumbnail_url=character['img_url'],
                            id=character['id'],
                            photo_url=character['img_url'],
                            caption=f"🌻 <b><a href='tg://user?id={user['id']}'>{user.get('first_name', user['id'])}</a></b>'s Character\n\n<b>{character['name']}</b> " + (f"<b>(x{character.get('count', 1)})</b>" if character.get('count', 1) > 1 else "") + f"\n<b>{character['anime']} ({anime_characters_guessed}/{total_anime_characters})</b>\n<b>{rarity}</b>\n<b>{character['id']}</b>",
                            parse_mode='HTML'
                        )
                    )
                    added_characters.add(character['name'])

            await update.inline_query.answer(results, next_offset=next_offset)
        else:
            await update.inline_query.answer([InlineQueryResultArticle(
                id='notfound', 
                title="User not found", 
                input_message_content=InputTextMessageContent("User not found")
            )])
    else:
        cursor = collection.find({}).skip(offset).limit(51)
        all_characters = await cursor.to_list(length=51)
        if len(all_characters) > 50:
            all_characters = all_characters[:50]
            next_offset = str(offset + 50)
        else:
            next_offset = None

        results = []
        for character in all_characters:
            users_with_character = await user_collection.find({'characters.id': character['id']}).to_list(length=100)
            total_guesses = sum(character.get("count", 1) for user in users_with_character)

            # Get the character's rarity
            rarity = character.get('rarity', "Don't have rarity.. Coz u Guessed before implement rarity.. in this bot")

            results.append(
                InlineQueryResultPhoto(
                    thumbnail_url=character['img_url'],
                    id=character['id'],
                    photo_url=character['img_url'],
                    caption=f"<b>Look at this character!</b>\n\n⟹ <b>{character['name']}</b>\n⟹ <b>{character['anime']}</b>\n<b>Rarity:</b> {rarity}\n🆔: {character['id']}\n\n<b>Guessed {total_guesses} times In Globally</b>",
                    parse_mode='HTML'
                )
            )
        await update.inline_query.answer(results, next_offset=next_offset)

def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6656458442:AAGJ1nKC2qil9SMU3NbElluHSmHJrN8oZsg").build()

    # on different commands - answer in Telegram
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_counter, block=False))
    application.add_handler(CommandHandler(["guess", "grab", "protecc", "collect"], guess, block=False))
    application.add_handler(CommandHandler(["changetime"], change_time, block=False))
    application.add_handler(CommandHandler('grouptop', group_leaderboard))
    application.add_handler(CallbackQueryHandler(group_leaderboard_button, pattern='^group_leaderboard_myrank$'))
    application.add_handler(CommandHandler('globaltop', leaderboard))
    application.add_handler(CallbackQueryHandler(leaderboard_button, pattern='^leaderboard_'))
    application.add_handler(InlineQueryHandler(inlinequery, block=False))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
