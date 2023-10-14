import asyncio
from pyrogram import Client, filters
from pymongo import MongoClient
import requests
import re
import os
import uuid
import time

# Connect to MongoDB
client = MongoClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
db = client['Waifusss']
collection = db['anime_charactersss']
user_collection = db["user_collectionnn"]
group_collection = db["group_collection"]

# Initialize Pyrogram Client
api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6430015242:AAG5eGK4MYd9-58PjYfJZy0LhcfMvpWly1I'
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

sudo_users = [6404226395]  # Add more sudo user IDs to this list if needed
channel_id = -1001683394959

COMMAND_HANDLER = ". /".split()
group_message_counts = {}

@app.on_message(filters.command("ping"))
async def ping_handler(_, message):
    start_time = time.time()
    reply = await message.reply_text("Pinging...")
    end_time = time.time()
    await reply.edit_text(f"Pong! {round((end_time - start_time) * 1000)} ms")

@app.on_message(filters.command("upload"))
async def upload_handler(_, message):
    # Check if the user is a sudo user
    if message.from_user.id in sudo_users:
        msg = message.text.split(' ')
        if len(msg) == 4:
            img_url, character_name, anime_name = msg[1], msg[2].replace('-', ' ').title(), msg[3].replace('-', ' ').title()
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
                await app.send_photo(channel_id, file_name, caption=caption)
                
                # Delete image file
                os.remove(file_name)
            else:
                await message.reply_text("Invalid image URL.")
        else:
            await message.reply_text("Incorrect format. Use /upload img_url character-name anime-name")
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
            
            await message.reply_text(f"{character['character_name']} deleted successfully.")
        else:
            await message.reply_text("Character not found.")
    else:
        await message.reply_text("Only sudo users can use this command.")


@app.on_message(filters.command("changetime"))
async def changetime_handler(_, message):
    # Check if the user is a group admin
    admins = []
    async for admin in app.get_chat_members(message.chat.id, filter="administrators"):
        admins.append(admin.user.id)
    if message.from_user.id in admins:
        msg = message.text.split(' ')
        if len(msg) < 2:
            await message.reply_text("Please provide a new time. Use /changetime new_time")
            return

        new_time = int(msg[1])
        # Save new time to MongoDB
        group_collection.update_one({'id': message.chat.id}, {"$set": {'time': new_time}}, upsert=True)
        await message.reply_text(f"Time changed successfully to {new_time} messages.")
    else:
        await message.reply_text("Only group administrators can use this command.")

@app.on_message(filters.group)
async def group_message_handler(_, message):
    group = group_collection.find_one({'id': message.chat.id})
    if not group:
        # If the group is not in the database, add it with a default time of 100 messages
        group_collection.insert_one({'id': message.chat.id, 'time': 10, 'count': 0})
        group = group_collection.find_one({'id': message.chat.id})

    # Decrement the message count
    group_collection.update_one({'id': message.chat.id}, {"$inc": {'count': -1}})
    
    if group['count'] <= 0:
        character = collection.find_one()
        if character:
            # Download image
            response = requests.get(character['img_url'])
            file_name = os.path.join('image.jpg')
            with open(file_name, 'wb') as f:
                f.write(response.content)

            # Send to group
            caption = "Collect The Character"
            await app.send_photo(message.chat.id, file_name, caption=caption)

            # Delete image file
            if os.path.exists(file_name):
                os.remove(file_name)

            # Reset message count
            group_collection.update_one({'id': message.chat.id}, {"$set": {'count': group['time']}})

app.run()

