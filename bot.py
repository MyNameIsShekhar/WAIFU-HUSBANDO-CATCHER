from telethon import TelegramClient, events
from motor.motor_asyncio import AsyncIOMotorClient
import urllib.request

# Initialize MongoDB client
client = AsyncIOMotorClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')
db = client['anime_db']
collection = db['characters']

# Initialize Telegram client
api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6656458442:AAGJ1nKC2qil9SMU3NbElluHSmHJrN8oZsg'

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern='/upload'))
async def upload_handler(event):
    # Check if the user is a sudo user
    if event.message.from_id not in SUDO_USERS:
        await event.reply("Sorry, you don't have permission to use this command.")
        return

    # Parse the message
    parts = event.message.text.split(' ')
    if len(parts) != 4:
        await event.reply("Invalid format. Please use: /upload img_url anime_name character_name")
        return

    _, img_url, anime_name, character_name = parts

    # Check if the image URL is valid
    try:
        urllib.request.urlopen(img_url)
    except (ValueError, IOError):
        await event.reply("Invalid image URL.")
        return

    # Store in MongoDB
    character = {
        'anime_name': anime_name.replace('-', ' '),
        'character_name': character_name.replace('-', ' '),
        'img_url': img_url,
    }
    await collection.insert_one(character)

    await event.reply("Successfully uploaded.")

bot.run_until_disconnected()
