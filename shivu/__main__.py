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
from shivu.modules import ALL_MODULES
from shivu import application 
from shivu import db

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



for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)

    


async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)

    
    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

     
    async with lock:
        # Get message frequency and counter for this chat from the database
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get('message_frequency', 100)
            message_counter = chat_frequency.get('message_counter', 0)
        else:
        
            message_frequency =100
            message_counter = 0

        
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

    # RED FLAG
    if chat_id in first_correct_guesses:
        await update.message.reply_text(f'❌️ Already guessed by Someone..So Try Next Time Bruhh')
        return

    # Check if guess is correct
    guess = ' '.join(context.args).lower() if context.args else ''
    
    if guess.startswith("&") or guess.startswith("and"):
        await update.message.reply_text("You can't start your guess with '&' or 'and'.")
        return
        
    if guess and guess in last_characters[chat_id]['name'].lower():
        # Set the flag that someone has guessed correctly
        first_correct_guesses[chat_id] = user_id
        
        global_count = await user_totals_collection.find_one_and_update(
            {'id': 'global'},
            {'$inc': {'count': 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        
        group_user = await group_user_totals_collection.find_one({'group_id': chat_id, 'user_id': user_id})
        if group_user:
            
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != group_user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != group_user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await group_user_totals_collection.update_one({'group_id': chat_id, 'user_id': user_id}, {'$set': update_fields})
            await group_user_totals_collection.update_one({'group_id': chat_id, 'user_id': user_id}, {'$inc': {'total_count': 1}})
        elif hasattr(update.effective_user, 'username'):
            
            await group_user_totals_collection.insert_one({
                'group_id': chat_id,
                'user_id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'total_count': 1  
            })

        
        user = await user_collection.find_one({'id': user_id})
        if user:
            
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
                
                    
            else:
                
                last_characters[chat_id]['count'] = 1
                await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})

                
            
      
        elif hasattr(update.effective_user, 'username'):
            
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
                'total_count': 1  
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
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    if query.isdigit():
        user = await user_collection.find_one({'id': int(query)})

        if user:
            characters = user['characters'][offset:offset+50]
            if len(characters) > 50:
                characters = characters[:50]
                next_offset = str(offset + 50)
            else:
                next_offset = None

            results = []
            added_characters = set()
            for character in characters:
                if character['name'] not in added_characters:
                    anime_characters_guessed = sum(c['anime'] == character['anime'] for c in user['characters'])
                    total_anime_characters = await collection.count_documents({'anime': character['anime']})

                    rarity = character.get('rarity', "Don't have rarity.. ")

                    results.append(
                        InlineQueryResultPhoto(
                            thumbnail_url=character['img_url'],
                            id=character['id'],
                            photo_url=character['img_url'],
                            caption=f"🌻 <b><a href='tg://user?id={user['id']}'>{user.get('first_name', user['id'])}</a></b>'s Character\n\n🌸: <b>{character['name']}</b> " + (f"(x{character.get('count', 'only one')})") + f"\n🏖️: <b>{character['anime']} ({anime_characters_guessed}/{total_anime_characters})</b>\n<b>{rarity}</b>\n\n🆔: <b>{character['id']}</b>",
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
    else: # This line was indented incorrectly
        cursor = collection.find({'$or': [{'anime': {'$regex': query, '$options': 'i'}}, {'name': {'$regex': query, '$options': 'i'}}]}).skip(offset).limit(51)
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

            rarity = character.get('rarity', "Don't have rarity...")

            results.append(
                InlineQueryResultPhoto(
                    thumbnail_url=character['img_url'],
                    id=character['id'],
                    photo_url=character['img_url'],
                    caption=f"<b>Look at this character!</b>\n\n🌸 <b>{character['name']}</b>\n🏖️ <b>{character['anime']}</b>\n<b>{rarity}</b>\n🆔: {character['id']}\n\n<b>Guessed {total_guesses} times In Globally</b>",
                    parse_mode='HTML'
                )
            )
        await update.inline_query.answer(results, next_offset=next_offset)


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

    # Remove the character from the sender's collection
    await user_collection.update_one({'id': sender_id}, {'$pull': {'characters': {'id': character_id}}})

    # Add the character to the receiver's collection
    receiver = await user_collection.find_one({'id': receiver_id})

    if receiver:
        character_in_collection = next((character for character in receiver['characters'] if character['id'] == character_id), None)

        if character_in_collection:
            await user_collection.update_one({'id': receiver_id, 'characters.id': character_id}, {'$inc': {'characters.$.count': 1}})
        else:
            await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': character}})
    else:
        # Create new user document
        await user_collection.insert_one({
            'id': receiver_id,
            'username': update.message.reply_to_message.from_user.username,
            'first_name': update.message.reply_to_message.from_user.first_name,
            'characters': [character],
            'total_count': 1  
        })

    await update.message.reply_text(f"You have successfully gifted your character to {update.message.reply_to_message.from_user.first_name}!")

async def harem(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('You have not guessed any characters yet.')
        return


    characters = sorted(user['characters'], key=lambda x: x['anime'])

    grouped_characters = {k: list(v) for k, v in groupby(characters, key=lambda x: x['anime'])}

   #start 
    harem_message = f"<b>{update.effective_user.first_name}'s Harem</b>\n\n"

    
    for anime, characters in list(grouped_characters.items())[:5]:
        # Get the total number of characters from this anime
        total_characters = await collection.count_documents({'anime': anime})

       #middle 
        harem_message += f'🏖️ <b>{anime} - ({len(characters)} / {total_characters})</b>\n'
        harem_message += '⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋\n'

        
        characters = sorted(characters, key=lambda x: x['id'])[:2]
        
        
        for character in characters:
            count = character.get('count', "only one")
            rarity = character.get('rarity', "Don't have rarity...") # Get the character's rarity
            
            harem_message += f'🆔️ <b>{character["id"]}</b>| 🫧 {rarity} | <b>🌸 {character["name"]} × {count}</b>\n'
            
            harem_message += '⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋\n'

        harem_message += '\n'
        total_count = len(user['characters'])
    
    
    keyboard = [[InlineKeyboardButton(f"See All Characters ({total_count})", switch_inline_query_current_chat=str(user_id))]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    
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
    
    
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_counter, block=False))
    application.add_handler(CommandHandler(["guess", "grab", "protecc", "collect"], guess, block=False))
    application.add_handler(CommandHandler(["changetime"], change_time, block=False))
    application.add_handler(InlineQueryHandler(inlinequery, block=False))
    application.add_handler(CommandHandler('fav', fav, block=False))
    application.add_handler(CommandHandler("give", gift,block=False))
    application.add_handler(CommandHandler("collection", harem,block=False))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
