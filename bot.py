from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient
import re
import aiohttp
import asyncio
from datetime import datetime
import time
from random import randint


db = AsyncIOMotorClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')
collection = db['anime_db']['anime_collection']
group_collection = db['group_collection']
user_collection = db['user_collectionn']
# Initialize Pyrogram Client
api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6430015242:AAG5eGK4MYd9-58PjYfJZy0LhcfMvpWly1I'
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

last_character_sent = {}# Store the ID of the last character sent in each group
first_collected_by = {}

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
@bot.on_message(filters.command('ping'))
async def ping(client, message):
    start = time.time()
    sent_message = await message.reply("Pong!")
    end = time.time()
    elapsed_ms = (end - start) * 1000  # convert to milliseconds
    await sent_message.edit_text(f"Pong! Message speed: {int(elapsed_ms)} milliseconds")


@bot.on_message(filters.command('upload'))
async def upload(client, message):
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

@bot.on_message(filters.command('delete'))
async def delete(client, message):
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
