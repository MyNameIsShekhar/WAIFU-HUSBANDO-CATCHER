from telethon import TelegramClient, events
from pymongo import MongoClient
import requests
import re
import os


sudo_users = [6404226395]
# Connect to MongoDB
client = MongoClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')
db = client['animeDB']
collection = db['characters']

# Initialize Telegram Client
api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6656458442:AAGJ1nKC2qil9SMU3NbElluHSmHJrN8oZsg'
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern='/upload'))
async def upload_handler(event):
    # Check if the user is a sudo user
    if event.message.from_id in int(sudo_users):
        msg = event.message.text.split(' ')
        if len(msg) == 4:
            img_url, anime_name, character_name = msg[1], msg[2].replace('-', ' '), msg[3].replace('-', ' ')
            # Check if the URL is valid
            if re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', img_url):
                # Insert into MongoDB
                character_doc = {
                    "anime_name": anime_name,
                    "character_name": character_name,
                    "img_url": img_url,
                    "added_by": event.message.from_id
                }
                collection.insert_one(character_doc)
                await event.reply("Successfully uploaded.")
                
                # Download image
                response = requests.get(img_url)
                file_name = os.path.join('/tmp', 'image.jpg')
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                
                # Send to channel
                channel_id = -1001670772912  # Replace with your channel ID
                channel = await bot.get_entity(channel_id)
                user_mention = f'<a href="tg://user?id={event.message.from_id}">User</a>'
                caption = f'{user_mention} added a new character:\n\n' \
                          f'Anime: {anime_name}\n' \
                          f'Character: {character_name}'
                await bot.send_file(channel, file=file_name, caption=caption)
                
                # Delete image file
                os.remove(file_name)
            else:
                await event.reply("Invalid image URL.")
        else:
            await event.reply("Incorrect format. Use /upload img_url anime-name character-name")
    else:
        await event.reply("Only sudo users can use this command.")

bot.run_until_disconnected()
