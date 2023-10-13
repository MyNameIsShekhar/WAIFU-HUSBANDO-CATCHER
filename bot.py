import asyncio
from pyrogram import Client, filters
from pymongo import MongoClient
import requests
import re
import os
import uuid

# Connect to MongoDB
client = MongoClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
db = client['Waifusss']
collection = db['anime_charactersss']
user_collection = db["user_collectionnn"]


# Initialize Pyrogram Client
api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6430015242:AAG5eGK4MYd9-58PjYfJZy0LhcfMvpWly1I'
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

sudo_users = [6404226395]  # Add more sudo user IDs to this list if needed
channel_id = -1001670772912
@app.on_message(filters.command("upload"))
async def upload_handler(_, message):
    # Check if the user is a sudo user
    if message.from_user.id in sudo_users:
        msg = message.text.split(' ')
        if len(msg) == 4:
            img_url, anime_name, character_name = msg[1], msg[2].replace('-', ' ').title(), msg[3].replace('-', ' ').title()
            # Check if the URL is valid
            if re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', img_url):
                # Generate unique ID for the character
                character_id = str(collection.count_documents({}) + 1).zfill(4)
            

                # Insert into MongoDB
                character = {
                    "id": character_id,
                    "anime_name": anime_name,
                    "character_name": character_name,
                    "img_url": img_url,
                    "added_by": message.from_user.id
                }
                collection.insert_one(character)
                await message.reply_text("Successfully uploaded.")
                
                # Download image
                response = requests.get(img_url)
                file_name = os.path.join('/tmp', 'image.jpg')
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                
                # Send to channel
                 # Replace with your channel ID
                caption = f'{message.from_user.mention} added a new character:\n\n' \
                          f'**ID**: {character_id}\n' \
                          f'**Anime**: {anime_name}\n' \
                          f'**Character**: {character_name}'
                sent_message = await app.send_photo(channel_id, file_name, caption=caption)
                collection.update_one({'id': character_id}, {'$set': {'message_id': message.message_id}})
    
                # Delete image file
                os.remove(file_name)
            else:
                await message.reply_text("Invalid image URL.")
        else:
            await message.reply_text("Incorrect format. Use /upload img_url anime-name character-name")
    else:
        await message.reply_text("Only sudo users can use this command.")

@app.on_message(filters.command("delete"))
async def delete_handler(_, message):
    if message.from_user.id in sudo_users:
        msg = message.text.split(' ')
        if len(msg) < 2:
            await message.reply_text("Please provide a character ID. Use /delete character_id")
            return

        character_id = msg[1]
        character = collection.find_one({'id': character_id})
        if character:
            # Delete from MongoDB
            collection.delete_one({'id': character_id})
            
            # Delete from channel
            if 'message_id' in character:
                await app.delete_messages(character['message_id'])
            
            await message.reply_text(f"{character['character_name']} deleted successfully.")
        else:
            await message.reply_text("Character not found.")
    else:
        await message.reply_text("Only sudo users can use this command.")

                    
                    


app.run()

