from telethon import TelegramClient, events
from motor.motor_asyncio import AsyncIOMotorClient
import urllib.request
import random
# Initialize MongoDB client
client = AsyncIOMotorClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')
db = client['anime_db']
collection = db['characters']

# Initialize Telegram client
api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6656458442:AAGJ1nKC2qil9SMU3NbElluHSmHJrN8oZsg'

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Generate a unique 4-digit number
def generate_unique_id():
    while True:
        unique_id = random.randint(1000, 9999)
        if collection.count_documents({'id': unique_id}) == 0:
            return unique_id

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
        'id': generate_unique_id(),
        'anime_name': anime_name.replace('-', ' '),
        'character_name': character_name.replace('-', ' '),
        'img_url': img_url,
    }
    await collection.insert_one(character)

    # Send the image with caption to the channel and save the message ID
    message = await bot.send_file(
        -1001683394959,
        file=img_url,
        caption=f"ID: {character['id']}\nAnime: {character['anime_name']}\nCharacter: {character['character_name']}"
    )
    await collection.update_one({'id': character['id']}, {'$set': {'message_id': message.id}})

    await event.reply("Successfully uploaded.")

@bot.on(events.NewMessage(pattern='/delete'))
async def delete_handler(event):
    # Check if the user is a sudo user
    if event.message.from_id not in SUDO_USERS:
        await event.reply("Sorry, you don't have permission to use this command.")
        return

    # Parse the message
    parts = event.message.text.split(' ')
    if len(parts) != 2:
        await event.reply("Invalid format. Please use: /delete id")
        return

    _, id_str = parts
    id = int(id_str)

    # Delete from MongoDB and from the channel
    character = await collection.find_one({'id': id})
    if character is not None:
        await collection.delete_one({'id': id})
        await bot.delete_messages(-1001683394959, character['message_id'])
        await event.reply("Successfully deleted.")
    else:
        await event.reply("Character not found.")

bot.run_until_disconnected()

