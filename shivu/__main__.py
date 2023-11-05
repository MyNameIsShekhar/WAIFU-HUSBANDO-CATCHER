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
import re
import math
from shivu.modules import ALL_MODULES
from shivu import application 
from shivu import db

collection = db['anime_characters_lol']


user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]

group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']



sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651','5813403535', '6393627898', '5952787198', '6614280216','6248411931','5216262234','1608353423']



locks = {}
message_counters = {}
spam_counters = {}

last_characters = {}

sent_characters = {}


first_correct_guesses = {}

message_counts = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)


last_user = {}
warned_users = {}

async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        # Get message frequency for this chat from the database
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get('message_frequency', 70)
        else:
            message_frequency = 70

        # Check if the last 6 messages were sent by the same user
        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                # If the user has been warned in the last 10 minutes, ignore their messages
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    # Warn the user and record the time of the warning
                    await update.message.reply_text('Spammer Lel...your messages will be ignored for 10 minutes.')
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        # Increment message count for this chat
        if chat_id in message_counts:
            message_counts[chat_id] += 1
        else:
            message_counts[chat_id] = 1

        # Send image after every message_frequency messages
        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)
            # Reset counter for this chat
            message_counts[chat_id] = 0
            
async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id


    all_characters = list(await collection.find({}).to_list(length=None))
    
    
    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    
    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    
    character = random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])

    
    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    
    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption="""***A New Character Has Just Appeared Use /guess [name]!👒
And Add This Character In Your Collection***""",
        parse_mode='Markdown')
    



async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await update.message.reply_text(f'❌️ Already guessed by Someone..So Try Next Time Bruhh')
        return

    guess = ' '.join(context.args).lower() if context.args else ''
    
    if "&" in guess or "and" in guess.lower():
        await update.message.reply_text("You can't use '&' or 'and' in your guess.")
        return
        
    # Split the character's name into parts by space
    name_parts = last_characters[chat_id]['name'].lower().split()

    # Check if the guess is the full name of the character in any order, or any part of the name exactly
    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):
        # Rest of the function...

    
        first_correct_guesses[chat_id] = user_id
        
        user = await user_collection.find_one({'id': user_id})
        if user:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await user_collection.update_one({'id': user_id}, {'$set': update_fields})
            
            await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
      
        elif hasattr(update.effective_user, 'username'):
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
            })

        # Update the group leaderboard
        group_user_total = await group_user_totals_collection.find_one({'user_id': user_id, 'group_id': chat_id})
        if group_user_total:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != group_user_total.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != group_user_total.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$set': update_fields})
            
            await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$inc': {'count': 1}})
      
        else:
            await group_user_totals_collection.insert_one({
                'user_id': user_id,
                'group_id': chat_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'count': 1,
            })


        # Update the top global groups leaderboard
        group_info = await top_global_groups_collection.find_one({'group_id': chat_id})
        if group_info:
            update_fields = {}
            if update.effective_chat.title != group_info.get('group_name'):
                update_fields['group_name'] = update.effective_chat.title
            if update_fields:
                await top_global_groups_collection.update_one({'group_id': chat_id}, {'$set': update_fields})
            
            await top_global_groups_collection.update_one({'group_id': chat_id}, {'$inc': {'count': 1}})
      
        else:
            await top_global_groups_collection.insert_one({
                'group_id': chat_id,
                'group_name': update.effective_chat.title,
                'count': 1,
            })


        await update.message.reply_text(f'<b>Congratulations 🪼! <a href="tg://user?id={user_id}">{update.effective_user.first_name}</a> \nYou Got New Character 💮</b> \n\n<b>👒 Character name: {last_characters[chat_id]["name"]}</b> \n<b>♋ Anime: {last_characters[chat_id]["anime"]}</b> \n<b>🫧 Rairty: {last_characters[chat_id]["rarity"]}</b>\n\n<b>This character has been added to your harem now do /collection to check your new character</b>', parse_mode='HTML')

    else:
        await update.message.reply_text('Incorrect guess. Try again.')




async def change_time(update: Update, context: CallbackContext) -> None:
    
    user = update.effective_user
    chat = update.effective_chat
    member = await chat.get_member(user.id)

    if member.status not in ('administrator', 'creator'):
        await update.message.reply_text('You do not have permission to use this command.')
        return
    try:
        
        args = context.args
        if len(args) != 1:
            await update.message.reply_text('Incorrect format. Please use: /changetime NUMBER')
            return

        
        new_frequency = int(args[0])
        if new_frequency < 100:
            await update.message.reply_text('The message frequency must be greater than or equal to 100.')
            return

        
        chat_frequency = await user_totals_collection.find_one_and_update(
            {'chat_id': str(chat.id)},
            {'$set': {'message_frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        await update.message.reply_text(f'Successfully changed character appearance frequency to every {new_frequency} messages.')
    except Exception as e:
        await update.message.reply_text('Failed to change character appearance frequency.')

async def inlinequery(update: Update, context: CallbackContext) -> None:
    import time
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    if query.isdigit():
        user = await user_collection.find_one({'id': int(query)})

        if user:
            characters = list({v['id']:v for v in user['characters']}.values())[offset:offset+50]
            if len(characters) > 50:
                characters = characters[:50]
                next_offset = str(offset + 50)
            else:
                next_offset = str(offset + len(characters))

            results = []
            for character in characters:
                anime_characters_guessed = sum(c['anime'] == character['anime'] for c in user['characters'])
                total_anime_characters = await collection.count_documents({'anime': character['anime']})

                rarity = character.get('rarity', "Don't have rarity.. ")

                results.append(
                    InlineQueryResultPhoto(
                        thumbnail_url=character['img_url'],
                        id=f"{character['id']}_{time.time()}",
                        photo_url=character['img_url'],
                        caption=f"🌻 <b><a href='tg://user?id={user['id']}'>{user.get('first_name', user['id'])}</a></b>'s Character\n\n🌸: <b>{character['name']}</b>\n🏖️: <b>{character['anime']} ({anime_characters_guessed}/{total_anime_characters})</b>\n<b>{rarity}</b>\n\n🆔: <b>{character['id']}</b>",
                        parse_mode='HTML'
                    )
                )

            await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)
        else:
            await update.inline_query.answer([InlineQueryResultArticle(
                id='notfound', 
                title="User not found", 
                input_message_content=InputTextMessageContent("User not found")
            )], cache_time=5)
    else:
        
        # If the query is empty, fetch all characters from the database
        if not query:
            cursor = collection.find().skip(offset).limit(50)
        else:
            # Split the query into user ID and search term
            parts = query.split(' ', 1)

            if len(parts) > 1 and parts[0].isdigit():
                user_id, search_term = parts

                # Fetch the user from the database
                user = await user_collection.find_one({'id': int(user_id)})

                if user:
                    # Filter the user's characters based on the search term
                    cursor = [c for c in user['characters'] if search_term.lower() in c['name'].lower() or search_term.lower() in c['anime'].lower()]
                else:
                    cursor = []
            else:
                cursor = collection.find({'$or': [{'anime': {'$regex': query, '$options': 'i'}}, {'name': {'$regex': query, '$options': 'i'}}]}).skip(offset).limit(50)

        all_characters = cursor if isinstance(cursor, list) else await cursor.to_list(length=None)
        next_offset = str(offset + len(all_characters))

        results = []
        for character in all_characters:
            users_with_character = await user_collection.find({'characters.id': character['id']}).to_list(length=100)
            total_guesses = sum(character.get("count", 1) for user in users_with_character)

            rarity = character.get('rarity', "Don't have rarity...")

            results.append(
                InlineQueryResultPhoto(
                    thumbnail_url=character['img_url'],
                    id=f"{character['id']}_{time.time()}",
                    photo_url=character['img_url'],
                    caption=f"<b>Look at this character!</b>\n\n🌸 <b>{character['name']}</b>\n🏖️ <b>{character['anime']}</b>\n<b>{rarity}</b>\n🆔: {character['id']}\n\n<b>Guessed {total_guesses} times In Globally</b>",
                    parse_mode='HTML'
                )
            )
        await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    
    if not context.args:
        await update.message.reply_text('Please provide a character ID.')
        return

    character_id = context.args[0]

    
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('You have not guessed any characters yet.')
        return

    
    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('This character is not in your collection.')
        return

    
    user['favorites'] = [character_id]

    
    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})

    await update.message.reply_text(f'Character {character["name"]} has been added to your favorites.')





async def gift(update: Update, context: CallbackContext) -> None:
    sender_id = update.effective_user.id

    if not update.message.reply_to_message:
        await update.message.reply_text("You need to reply to a user's message to gift a character!")
        return

    receiver_id = update.message.reply_to_message.from_user.id

    if sender_id == receiver_id:
        await update.message.reply_text("You can't gift a character to yourself!")
        return

    if not context.args:
        await update.message.reply_text("You need to provide a character ID!")
        return

    character_id = context.args[0]

    sender = await user_collection.find_one({'id': sender_id})

    character = next((character for character in sender['characters'] if character['id'] == character_id), None)

    if not character:
        await update.message.reply_text("You don't have this character in your collection!")
        return

    # Remove only one instance of the character from the sender's collection
    sender['characters'].remove(character)
    await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})

    # Add the character to the receiver's collection
    receiver = await user_collection.find_one({'id': receiver_id})

    if receiver:
        await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': character}})
    else:
        # Create new user document
        await user_collection.insert_one({
            'id': receiver_id,
            'username': update.message.reply_to_message.from_user.username,
            'first_name': update.message.reply_to_message.from_user.first_name,
            'characters': [character],
        })

    await update.message.reply_text(f"You have successfully gifted your character to {update.message.reply_to_message.from_user.first_name}!")




async def harem(update: Update, context: CallbackContext, page=0) -> None:
    user_id = update.effective_user.id

    user = await user_collection.find_one({'id': user_id})
    if not user:
        if update.message:
            await update.message.reply_text('You have not guessed any characters yet.')
        else:
            await update.callback_query.edit_message_text('You have not guessed any characters yet.')
        return

    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))

    # Group the characters by id and count the occurrences
    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}

    # Remove duplicates
    unique_characters = list({character['id']: character for character in characters}.values())

    # Calculate the total number of pages
    total_pages = math.ceil(len(unique_characters) / 15)  # Number of characters divided by 15 characters per page, rounded up

    # Check if page is within bounds
    if page < 0 or page >= total_pages:
        page = 0  # Reset to first page if out of bounds

    harem_message = f"<b>{update.effective_user.first_name}'s Harem - Page {page+1}/{total_pages}</b>\n\n"

    # Get the characters for the current page
    current_characters = unique_characters[page*15:(page+1)*15]

    # Group the current characters by anime
    current_grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

    for anime, characters in current_grouped_characters.items():
        harem_message += f'\n🏖️ <b>{anime} {len(characters)}/{await collection.count_documents({"anime": anime})}</b>\n'

        for character in characters:
            
            count = character_counts[character['id']]  # Get the count from the character_counts dictionary
            harem_message += f'{character["id"]} {character["name"]} ×{count}\n'

         # Add a line break after each anime group

    total_count = len(user['characters'])
    
    keyboard = [[InlineKeyboardButton(f"See All Characters ({total_count})", switch_inline_query_current_chat=str(user_id))]]

    # Add navigation buttons if there are multiple pages
    if total_pages > 1:
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("Prev", callback_data=f"harem:{page-1}:{user_id}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next", callback_data=f"harem:{page+1}:{user_id}"))
        keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    if 'favorites' in user and user['favorites']:
        # Get the favorite character
        fav_character_id = user['favorites'][0]
        fav_character = next((c for c in user['characters'] if c['id'] == fav_character_id), None)

        if fav_character and 'img_url' in fav_character:
            if update.message:
                await update.message.reply_photo(photo=fav_character['img_url'], parse_mode='HTML', caption=harem_message, reply_markup=reply_markup)
            else:
                # Check if the new caption is different from the existing one
                if update.callback_query.message.caption != harem_message:
                    await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup, parse_mode='HTML')
        else:
            if update.message:
                await update.message.reply_text(harem_message, parse_mode='HTML', reply_markup=reply_markup)
            else:
                # Check if the new text is different from the existing one
                if update.callback_query.message.text != harem_message:
                    await update.callback_query.edit_message_text(harem_message, parse_mode='HTML', reply_markup=reply_markup)
    else:
        # Check if the user's collection is not empty
        if user['characters']:
            # Get a random character from the user's collection
            random_character = random.choice(user['characters'])

            if 'img_url' in random_character:
                if update.message:
                    await update.message.reply_photo(photo=random_character['img_url'], parse_mode='HTML', caption=harem_message, reply_markup=reply_markup)
                else:
                    # Check if the new caption is different from the existing one
                    if update.callback_query.message.caption != harem_message:
                        await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup, parse_mode='HTML')
            else:
                if update.message:
                    await update.message.reply_text(harem_message, parse_mode='HTML', reply_markup=reply_markup)
                else:
                    # Check if the new text is different from the existing one
                    if update.callback_query.message.text != harem_message:
                        await update.callback_query.edit_message_text(harem_message, parse_mode='HTML', reply_markup=reply_markup)
        else:
            if update.message:
                await update.message.reply_text("Your list is empty.")
            
      
      



    
async def harem_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    # Split the data to get the page number and user_id
    _, page, user_id = data.split(':')

    # Convert the page number and user_id to integers
    page = int(page)
    user_id = int(user_id)

    # Check if the user who clicked the button is the same as the user who owns the collection
    if query.from_user.id != user_id:
        await query.answer("Don't Stalk Other User's Harem.. lmao", show_alert=True)
        return

    # Call the harem function with the page number and user_id
    await harem(update, context, page)





def main() -> None:
    """Run bot."""
    
    
    application.add_handler(CommandHandler(["guess", "protecc", "collect", "grab", "hunt"], guess, block=False))
    application.add_handler(CommandHandler(["changetime"], change_time, block=False))
    application.add_handler(InlineQueryHandler(inlinequery, block=False))
    application.add_handler(CommandHandler('fav', fav, block=False))
    application.add_handler(CommandHandler("give", gift, block=False))
    application.add_handler(CommandHandler("collection", harem,block=False))
    
    harem_handler = CallbackQueryHandler(harem_callback, pattern='^harem')
    application.add_handler(harem_handler)
    
    
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
    
    

    application.run_polling( drop_pending_updates=True)
    
if __name__ == "__main__":
    main()
