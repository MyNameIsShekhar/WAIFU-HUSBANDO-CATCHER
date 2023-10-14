from aiogram import Bot, Dispatcher, types
from motor.motor_asyncio import AsyncIOMotorClient
import re
import aiohttp
from aiogram import executor
import asyncio
from datetime import datetime
import time

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





@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_all_messages(message: types.Message):
    # Check if the message is from a group
    if message.chat.type in (types.ChatType.GROUP, types.ChatType.SUPERGROUP):
        group_id = message.chat.id
        # Initialize the group settings if they don't exist
        if group_id not in group_settings:
            group_settings[group_id] = {'message_count': 0, 'time_interval': 100}
        # Increment the message count
        group_settings[group_id]['message_count'] += 1
        # If the message count reaches the time interval, send a character
        if group_settings[group_id]['message_count'] >= group_settings[group_id]['time_interval']:
            # Reset the message count
            group_settings[group_id]['message_count'] = 0
            # Get a random character from the database
            character = await collection.aggregate([{'$sample': {'size': 1}}]).to_list(length=1)
            character = character[0] if character else None
            if character:
                await bot.send_photo(
                    group_id,
                    character['img_url'],
                    caption=f"Collect the character with /collect {character['character_name']}"
                )

@dp.message_handler(commands=['changetime'])
async def change_time(message: types.Message):
    # Check if the user is an admin or the creator of the group
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status in (types.ChatMemberStatus.ADMINISTRATOR, types.ChatMemberStatus.CREATOR):
        try:
            _, time_interval = message.text.split(' ')
            time_interval = int(time_interval)
            if time_interval < 100:
                await message.reply("Time interval cannot be less than 100.")
                return
            # Change the time interval for the group
            group_settings[message.chat.id]['time_interval'] = time_interval
            await message.reply(f"Time interval changed to {time_interval}.")
        except Exception as e:
            await message.reply(f"Error: {str(e)}")
    else:
        await message.reply("You are not authorized to use this command.")


executor.start_polling(dp)
