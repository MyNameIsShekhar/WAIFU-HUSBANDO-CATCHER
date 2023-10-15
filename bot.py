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


@dp.message_handler(commands=['collect'])
async def collect(message: types.Message):
    group_id = message.chat.id
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    # Get the character name from the message
    _, character_name = message.text.split(' ', 1)
    character_name = character_name.lower()
    # Fetch a character from the database that matches the name
    character_doc = await collection.find_one({'character_name': re.compile(character_name, re.IGNORECASE)})
    


    # Fetch the user's document from the database
    user_doc = await user_collection.find_one({'_id': user_id})
    if user_doc:
        # Check if the user's first name has changed
        if user_doc.get('first_name') != user_first_name:
            # Update the user's first name in the database
            await user_collection.update_one({'_id': user_id}, {'$set': {'first_name': user_first_name}})
        
    else:
        # Create a new document for the user in the database
        await user_collection.insert_one({'_id': user_id, 'first_name': user_first_name, 'collected_characters': []})
    
    # Add the character to the user's collection in the database
    await user_collection.update_one({'_id': user_id}, {'$push': {'collected_characters': character_doc['_id']}}, upsert=True)
    
    # Fetch the updated document and count the number of times this specific character has been collected
    updated_user_doc = await user_collection.find_one({'_id': user_id})
    num_times_collected = updated_user_doc['collected_characters'].count(character_doc['_id'])
    
    await message.reply(f'<a href="tg://user?id={user_id}">{user_first_name}</a> Congrats! {character_name} is now in your collection. You have collected {character_name} {num_times_collected} times.', parse_mode='HTML')
    
    # Update the last character sent in this group to prevent others from collecting it
    last_character_sent[group_id] = None
    else:
        update.message.reply_text('Incorrect guess. Try again.')


   


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def send_image(message: types.Message):
    group_id = message.chat.id
    # Load the settings from the database
    doc = await group_collection.find_one({'_id': group_id})
    if doc is None:
        # Use default settings if no settings are found in the database
        doc = {'message_count': 0, 'time': 10, 'sent_images': []}
    else:
        # Check if 'time' key exists in the doc, if not set a default time
        if 'time' not in doc:
            doc['time'] = 10
        # Check if 'message_count' key exists in the doc, if not set it to 0
        if 'message_count' not in doc:
            doc['message_count'] = 0

    doc['message_count'] += 1
    if doc['message_count'] >= doc['time']:
        # Reset the message count and save it to the database immediately
        doc['message_count'] = 0
        await group_collection.update_one({'_id': group_id}, {'$set': {'message_count': doc['message_count']}}, upsert=True)
        
        # Fetch a random character from the database that hasn't been sent yet
        count = await collection.count_documents({})
        random_index = randint(0, count - 1)
        character_doc = await collection.find().skip(random_index).limit(1).to_list(length=1)
        
        # If all images have been sent, start from the beginning
        if not character_doc:
            doc['sent_images'] = []
            character_doc = await collection.find().to_list(length=None)

        character_doc = character_doc[0]
        
        # Send the image to the group and update last_character_sent for this group
        last_character_sent[group_id] = character_doc['_id']
        
        await bot.send_photo(
            group_id,
            character_doc['img_url'],
            caption=f"/collect this Character..And Add In Your Collection..",
            
        )
    else:
        # If no image was sent, save the updated message count to the database
        await group_collection.update_one({'_id': group_id}, {'$set': {'message_count': doc['message_count']}}, upsert=True)


executor.start_polling(dp)
