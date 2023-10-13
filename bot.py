import asyncio
from pyrogram import Client, filters
from pymongo import MongoClient
from telegraph import Telegraph, upload_file
import requests
import re
import os

# Connect to MongoDB
client = MongoClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')
db = client['animeDB']
collection = db['characters']

# Initialize Pyrogram Client
api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6430015242:AAG5eGK4MYd9-58PjYfJZy0LhcfMvpWly1I'
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Initialize Telegraph Client
telegraph = Telegraph()
telegraph.create_account(short_name='Anime')

sudo_users = [6404226395]  # Add more sudo user IDs to this list if needed
channel_id = -1001670772912

@app.on_message(filters.photo & filters.command("upload"))
async def upload_handler(_, message):
    # Check if the user is a sudo user
    if message.from_user.id in sudo_users:
        msg = message.caption.split(' ')
        if len(msg) == 2:
            anime_name, character_name = msg[0].replace('-', ' ').title(), msg[1].replace('-', ' ').title()
            
            # Download image
            img_url = message.photo.file_path
            response = requests.get(img_url)
            file_name = os.path.join('/tmp', 'image.jpg')
            with open(file_name, 'wb') as f:
                f.write(response.content)
            
            # Upload image to Telegraph
            telegraph_url = 'https://telegra.ph' + upload_file(file_name)[0]
            
            # Generate unique ID for the character
            character_id = str(collection.count_documents({}) + 1).zfill(4)
            
            # Insert into MongoDB
            character_doc = {
                "id": character_id,
                "anime_name": anime_name,
                "character_name": character_name,
                "img_url": telegraph_url,
                "added_by": message.from_user.id
            }
            collection.insert_one(character_doc)
            await message.reply_text("Successfully uploaded.")
            
            # Send to channel
              # Replace with your channel ID
            caption = f'{message.from_user.mention} added a new character:\n\n' \
                      f'**ID**: {character_id}\n' \
                      f'**Anime**: {anime_name}\n' \
                      f'**Character**: {character_name}'
            await app.send_photo(channel_id, file_name, caption=caption)
            
            # Delete image file
            os.remove(file_name)
        else:
            await message.reply_text("Incorrect format. Send photo with caption: /upload anime-name character-name")
    else:
        await message.reply_text("Only sudo users can use this command.")

app.run()
