from aiogram import Bot, Dispatcher, types
from motor.motor_asyncio import AsyncIOMotorClient
import re
import aiohttp
from aiogram import executor
import asyncio
from datetime import datetime
import time
from random import randint

bot =Bot('6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs')
dp = Dispatcher(bot)

client = AsyncIOMotorClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')
db = client['anime_db']
collection = db['anime_collection']
group_collection = db['group_collection']
user_collection = db['user_collectionn']

last_character_sent = {}# Store the ID of the last character sent in each group

group_settings = {}  # Store the settings for each group
CHANNEL_ID = -1001683394959
SUDO_USER_ID = [6404226395]

async def generate_id():
    for i in range(1, 10000):
        id = str(i).zfill(4)
        if not await collection.find_one({'_id': id}):
            return id
    return None

async def is_url_valid(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return response.status == 200
    except Exception:
        return False





@dp.message_handler(commands=['ping'])
async def ping(message: types.Message):
    start = time.time()
    sent_message = await message.reply("Pong!")
    end = time.time()
    elapsed_ms = (end - start) * 1000  # convert to milliseconds
    await sent_message.edit_text(f"Pong! Message speed: {int(elapsed_ms)} milliseconds")


@dp.message_handler(commands=['upload'])
async def upload(message: types.Message):
    if message.from_user.id in SUDO_USER_ID:
        try:
            _, img_url, character_name, anime_name = message.text.split(' ')
            character_name = character_name.replace('-', ' ').title()
            anime_name = anime_name.replace('-', ' '). title()
            # Validate the URL
            if not await is_url_valid(img_url):
                await message.reply("Invalid URL")
                return
            id = await generate_id()
            if id is None:
                await message.reply("Error: Database is full.")
                return
            doc = {
                '_id': id,
                'img_url': img_url,
                'anime_name': anime_name,
                'character_name': character_name
            }
            await collection.insert_one(doc)
            await message.reply("Successfully uploaded")
            # Send the information to the channel
            sent_message = await bot.send_photo(
                CHANNEL_ID,
                img_url,
                caption=f"<b>ID:</b> {id}\n<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime_name}",
                parse_mode='HTML'
            )
            # Save the message ID to the database
            await collection.update_one({'_id': id}, {'$set': {'channel_message_id': sent_message.message_id}})
        except Exception as e:
            await message.reply(f"Error: {str(e)}")
    else:
        await message.reply("You are not authorized to use this command.")

@dp.message_handler(commands=['delete'])
async def delete(message: types.Message):
    if message.from_user.id in SUDO_USER_ID:
        try:
            _, id = message.text.split(' ')
            # Find the character in the database
            doc = await collection.find_one({'_id': id})
            if doc is None:
                await message.reply("Character not found.")
                return
            # Delete the character from the database
            await collection.delete_one({'_id': id})
            # Delete the message from the channel
            await bot.delete_message(CHANNEL_ID, doc['channel_message_id'])
            await message.reply("Successfully deleted.")
        except Exception as e:
            await message.reply(f"Error: {str(e)}")
    else:
        await message.reply("You are not authorized to use this command.")

@dp.message_handler(commands=['new_time'])
async def new_time(message: types.Message):
    group_id = message.chat.id
    # Check if the user is a group administrator
    member = await bot.get_chat_member(group_id, message.from_user.id)
    if member.status not in ('administrator', 'creator'):
        await message.reply("You are not authorized to use this command.")
        return
    try:
        _, new_time = message.text.split(' ')
        new_time = int(new_time)
        if new_time < 100:
            await message.reply("Time cannot be less than 100.")
            return
        # Save the new time to the database
        await group_collection.update_one({'_id': group_id}, {'$set': {'time': new_time}}, upsert=True)
        await message.reply(f"Successfully changed the character appearance time to {new_time}.")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def send_image(message: types.Message):
    chat_id = message.chat.id

    # Get all characters
    all_characters = list(await collection.find({}).to_list(length=None))
    
    # Initialize sent characters list for this chat if it doesn't exist
    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    # Reset sent characters list if all characters have been sent
    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    # Select a random character that hasn't been sent yet
    character = random.choice([c for c in all_characters if c['_id'] not in sent_characters[chat_id]])

    # Add character to sent characters list and set as last sent character
    sent_characters[chat_id].append(character['_id'])
    last_characters[chat_id] = character

    # Reset first correct guess when a new character is sent
    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    # Send image with caption
    await bot.send_photo(
        chat_id,
        character['img_url'],
        caption="Use /collect Command And.. Collect This Character.."
    )
@dp.message_handler(commands=['collect'])
async def collect(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name

    # Check if a character has been sent in this chat yet
    if chat_id not in last_characters:
        return

    # If someone has already guessed correctly
    if chat_id in first_correct_guesses:
        await message.reply(f'❌️ Already collected by Someone..So Try Next Time Bruhh')
        return

    # Check if collect is correct
    collect = ' '.join(context.args).lower() if context.args else ''
    
    if collect and collect in last_characters[chat_id]['name'].lower():
        # Set the flag that someone has collected correctly
        first_correct_guesses[chat_id] = user_id

        # Add character to user's collection
        user = user_collection.find_one({'id': user_id})
        if user:
            # Update username if it has changed
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user['username']:
                user_collection.update_one({'id': user_id}, {'$set': {'username': update.effective_user.username}})
            # Increment count of character in user's collection
            character_index = next((index for (index, d) in enumerate(user['characters']) if d["id"] == last_characters[chat_id]["id"]), None)
            if character_index is not None:
                # Check if 'count' key exists and increment it, otherwise add it
                if 'count' in user['characters'][character_index]:
                    user['characters'][character_index]['count'] += 1
                else:
                    user['characters'][character_index]['count'] = 1
                user_collection.update_one({'id': user_id}, {'$set': {'characters': user['characters']}})
            else:
                # Add character to user's collection
                last_characters[chat_id]['count'] = 1
                user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
        elif hasattr(update.effective_user, 'username'):
            # Create new user document
            last_characters[chat_id]['count'] = 1
            user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'characters': [last_characters[chat_id]]
            })

        await message.reply(f'Congooo ✅️! <a href="tg://user?id={user_id}">{update.effective_user.first_name}</a> collected it right. The character is {last_characters[chat_id]["name"]} from {last_characters[chat_id]["anime"]}.', parse_mode='HTML')

    else:
        await message.reply('Incorrect collect. Try again.')
