from aiogram import Bot, Dispatcher, types
from motor.motor_asyncio import AsyncIOMotorClient
import re
import aiohttp
import asyncio

bot = Bot(token='6656458442:AAGJ1nKC2qil9SMU3NbElluHSmHJrN8oZsg')
dp = Dispatcher(bot)

client = AsyncIOMotorClient('mongodb://localhost:27017/')
db = client['anime_db']
collection = db['anime_collection']

CHANNEL_ID = -1001683394959

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

@dp.message_handler(commands=['upload'])
async def upload(message: types.Message):
    if message.from_user.id == SUDO_USER_ID:
        try:
            _, img_url, anime_name, character_name = message.text.split(' ')
            anime_name = anime_name.replace('-', ' ')
            character_name = character_name.replace('-', ' ')
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
            await bot.send_photo(
                CHANNEL_ID,
                img_url,
                caption=f"**ID:** {id}\n**Anime Name:** {anime_name}\n**Character Name:** {character_name}"
            )
        except Exception as e:
            await message.reply(f"Error: {str(e)}")
    else:
        await message.reply("You are not authorized to use this command.")

async def main():
    from aiogram import executor
    executor.start_polling(dp)

if __name__ == '__main__':
    
    asyncio.run(main())
