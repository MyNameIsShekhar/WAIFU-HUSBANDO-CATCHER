
from telethon import TelegramClient, events
from telegraph import Telegraph
from pymongo import MongoClient
import random
import string

# Initialize MongoDB
client =MongoClient('mongodb+srv://shuyaaaaa12:NvpoBuRp7MVPcAYA@cluster0.q2yycqx.mongodb.net/')
db = client['anime_db']
collection = db['anime_collection']

api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6347356084:AAHX7A8aY9fbtgCQ-8R16TRBKkCHtX4bMxA'

telegraph = Telegraph()
telegraph.create_account(short_name='anime')


@bot.on(events.NewMessage(pattern='/upload'))
async def upload_handler(event):
    if event.photo and event.message.split():
        # Generate unique character id
        while True:
            character_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if collection.find_one({'character_id': character_id}) is None:
                break

        # Upload photo to Telegraph and store in DB
        character_name, anime_name = event.message.split('-')
        response = telegraph.upload(event.photo)
        collection.insert_one({
            'character_id': character_id,
            'character_name': character_name,
            'anime_name': anime_name,
            'photo_url': response[0],
            'added_by': event.sender_id,
        })

        # Send message to channel with character info
        await bot.send_message(-1001670772912, f"New character added!\\nCharacter ID: {character_id}\\nCharacter Name: {character_name}\\nAnime Name: {anime_name}\\nAdded by: {event.sender.first_name}")
    else:
        await bot.send_message(event.chat_id, "Incorrect format. Please use /upload with a photo and the format 'character-name-anime-name'.")




bot.run_until_disconnected()

