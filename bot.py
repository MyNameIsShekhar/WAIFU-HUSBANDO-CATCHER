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
            _, img_url, anime_name, character_name = message.text.split(' ')
            character_name = character_name.replace('-', ' ')
            anime_name = anime_name.replace('-', ' ')
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
                caption=f"<b>ID:</b> {id}\n<b>Anime Name:</b> {anime_name}\n<b>Character Name:</b> {character_name}",
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
    global group_settings
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
        # Update the time in the group settings
        if group_id not in group_settings:
            group_settings[group_id] = {'message_count': 0}
        group_settings[group_id]['time'] = new_time
        # Save the new time to the database
        await group_collection.update_one({'_id': group_id}, {'$set': {'time': new_time}}, upsert=True)
        await message.reply(f"Successfully changed the character appearance time to {new_time}.")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

@dp.message_handler(content_types=types.ContentTypes.ANY)
async def send_image(message: types.Message):
    global group_settings
    group_id = message.chat.id
    if group_id not in group_settings:
        # Load the settings from the database
        doc = await group_collection.find_one({'_id': group_id})
        if doc is None:
            # Use default settings if no settings are found in the database
            group_settings[group_id] = {'message_count': 0, 'time': 10}
        else:
            group_settings[group_id] = {'message_count': 0, 'time': 10}
    group_settings[group_id]['message_count'] += 1
    if group_settings[group_id]['message_count'] >= group_settings[group_id]['time']:
        group_settings[group_id]['message_count'] = 0
        # Fetch a random character from the database
        count = await collection.count_documents({})
        random_index = randint(0, count - 1)
        doc = await collection.find().skip(random_index).limit(1).to_list(length=1)
        if doc:
            doc = doc[0]
            # Send the image to the group
            await bot.send_photo(
                group_id,
                doc['img_url'],
                caption=f"/collect this Character..And Add In Your Collection..",
                
            )





executor.start_polling(dp)
