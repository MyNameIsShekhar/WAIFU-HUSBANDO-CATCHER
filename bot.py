import importlib
from telegram import InputMediaPhoto
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent, InputMediaPhoto
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
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


user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]

group_user_totals_collection = db['group_user_totalssssss']



sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651','5813403535', '6393627898', '5952787198', '6614280216','6248411931','5216262234','1608353423']



locks = {}
message_counters = {}
spam_counters = {}

last_characters = {}

sent_characters = {}


first_correct_guesses = {}



    


async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)

    
    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

     
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
And Add This Character In Your Collection***""",
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
            
            
            character_in_collection = next((character for character in user['characters'] if character['id'] == last_characters[chat_id]['id']), None)
        
            if character_in_collection:
                await user_collection.update_one({'id': user_id, 'characters.id': last_characters[chat_id]['id']}, {'$inc': {'characters.$.count': 1}})
                
            # If the character is already in the collection, increment        
            else:
                
                last_characters[chat_id]['count'] = 1
                await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})

                
            # If the character is not in the collection, add it with a count of 1i
                 
      
        elif hasattr(update.effective_user, 'username'):
            # Create new user document with total_count initialized to 1
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
                'total_count': 1  # Initialize total_count
            })
        await update.message.reply_text(f'<b>Congratulations 🪼! <a href="tg://user?id={user_id}">{update.effective_user.first_name}</a> \nYou Got New Character 💮</b> \n\n<b>👒 Character name: {last_characters[chat_id]["name"]}</b> \n<b>♋ Anime: {last_characters[chat_id]["anime"]}</b> \n<b>🫧 Rairty: {last_characters[chat_id]["rarity"]}</b>\n\n<b>This character has been added to your harem now do /collection to check your new character</b>', parse_mode='HTML')

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
                    rarity = character.get('rarity', "Don't have rarity.. ")

                    
                    results.append(
                        InlineQueryResultPhoto(
                            thumbnail_url=character['img_url'],
                            id=character['id'],
                            photo_url=character['img_url'],
                            caption=f"🌻 <b><a href='tg://user?id={user['id']}'>{user.get('first_name', user['id'])}</a></b>'s Character\n\n<b>Name:</b> {character['name']} " + (f"(x{character.get('count', 1)})") + f"\n<b>Anime:</b> {character['anime']} ({anime_characters_guessed}/{total_anime_characters})\n<b>Rarity:<b> {rarity}</b>\n🆔: {character['id']}",
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
            rarity = character.get('rarity', "Don't have rarity...")

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
        
async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Check if an ID was provided
    if not context.args:
        await update.message.reply_text('Please provide a character ID.')
        return

    character_id = context.args[0]

    # Get the user document
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('You have not guessed any characters yet.')
        return

    # Check if the character is in the user's collection
    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('This character is not in your collection.')
        return

    # Replace the old favorite with the new one
    user['favorites'] = [character_id]

    # Update user document
    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})

    await update.message.reply_text(f'Character {character["name"]} has been added to your favorites.')



async def gift(update: Update, context: CallbackContext) -> None:
    # Get the sender's user ID
    sender_id = update.effective_user.id

    # Check if the user has replied to a message
    if not update.message.reply_to_message:
        await update.message.reply_text("You need to reply to a user's message to gift a character!")
        return

    # Get the receiver's user ID
    receiver_id = update.message.reply_to_message.from_user.id

    # Check if the sender and receiver are the same person
    if sender_id == receiver_id:
        await update.message.reply_text("You can't gift a character to yourself!")
        return

    # Check if a character ID was provided
    if not context.args:
        await update.message.reply_text("You need to provide a character ID!")
        return

    character_id = context.args[0]

    # Get the sender's characters
    sender = await user_collection.find_one({'id': sender_id})

    # Check if the sender has the character in their collection
    character = next((character for character in sender['characters'] if character['id'] == character_id), None)
    
    if not character:
        await update.message.reply_text("You don't have this character in your collection!")
        return

    # Remove the character from the sender's collection
    await user_collection.update_one({'id': sender_id}, {'$pull': {'characters': {'id': character_id}}})

    # Add the character to the receiver's collection
    receiver = await user_collection.find_one({'id': receiver_id})
    
    if receiver:
        await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': character}})
    else:
        # Create new user document with total_count initialized to 1
        await user_collection.insert_one({
            'id': receiver_id,
            'username': update.message.reply_to_message.from_user.username,
            'first_name': update.message.reply_to_message.from_user.first_name,
            'characters': [character],
            'total_count': 1  # Initialize total_count
        })

    await update.message.reply_text(f"You have successfully gifted your character to {update.message.reply_to_message.from_user.first_name}!")

async def harem(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Get the user's collection
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('You have not guessed any characters yet.')
        return

    # Get the list of characters and sort by anime name
    characters = sorted(user['characters'], key=lambda x: x['anime'])

    # Group the characters by anime
    grouped_characters = {k: list(v) for k, v in groupby(characters, key=lambda x: x['anime'])}

    # Start of the harem message
    harem_message = f"<b>See <a href='tg://user?id={user_id}'>{update.effective_user.first_name}</a>'s Letest 5 Characters</b>\n\n"

    # Iterate over the first five grouped characters
    for anime, characters in list(grouped_characters.items())[:5]:
        # Get the total number of characters from this anime
        total_characters = await collection.count_documents({'anime': anime})

        # Add the anime name and the number of collected characters to the message
        harem_message += f'<b>{anime} - ({len(characters)} / {total_characters})</b>\n'

        # Sort the characters by ID and take only the first two
        characters = sorted(characters, key=lambda x: x['id'])[:2]

        # Add the character details to the message
        for character in characters:
            count = character.get('count')
            rarity = character.get('rarity', "Don't have rarity...") # Get the character's rarity
            if count is not None:
                harem_message += f'<b>🆔️: {character["id"]}</b>\n<b>{character["name"]} × {count}</b>\n<b>{rarity}</b>\n'
            else:
                harem_message += f'<b>🆔️: {character["id"]}</b>\n<b>{character["name"]}</b>\n<b>{rarity}</b>\n'

        harem_message += '\n'
        total_count = len(user['characters'])
    # Create an InlineKeyboardButton named 'All Characters'
    keyboard = [[InlineKeyboardButton(f"See All Characters ({total_count})", switch_inline_query_current_chat=str(user_id))]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # If a favorite character is set, send its image with harem message as caption
    if 'favorites' in user and user['favorites']:
        fav_character_id = user['favorites'][0]
        fav_character = next((c for c in user['characters'] if c['id'] == fav_character_id), None)
        
        if fav_character and 'img_url' in fav_character:
            await update.message.reply_photo(photo=fav_character['img_url'], parse_mode='HTML', caption=harem_message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(harem_message, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(harem_message, parse_mode='HTML', reply_markup=reply_markup)

def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6420751168:AAEtf-OyEYLLTZM2c4LrhIroXPfvsW7KlM8").build()

    # on different commands - answer in Telegram
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_counter, block=False))
    application.add_handler(CommandHandler(["guess", "grab", "protecc", "collect"], guess, block=False))
    application.add_handler(CommandHandler(["changetime"], change_time, block=False))
    application.add_handler(CommandHandler('grouptop', group_leaderboard, block=False))
    application.add_handler(CallbackQueryHandler(group_leaderboard_button, pattern='^group_leaderboard_myrank$', block=False))
    application.add_handler(CommandHandler('globaltop', leaderboard, block=False))
    application.add_handler(CallbackQueryHandler(leaderboard_button, pattern='^leaderboard_',block=False))
    application.add_handler(InlineQueryHandler(inlinequery, block=False))
    application.add_handler(CommandHandler('fav', fav, block=False))
    application.add_handler(CommandHandler("gift", gift,block=False))
    application.add_handler(CommandHandler("collection", harem,block=False))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
