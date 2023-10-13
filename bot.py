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

@app.on_message(filters.group)
async def message_handler(_, message):
    group_id = message.chat.id
    group = group_collection.find_one({'id': group_id})

    if group is None:
        # This group doesn't exist in the database yet.
        # Create a new document for it.
        group = {'id': group_id, 'message_count': 0, 'character_time': 10}
        group_collection.insert_one(group)

    # Increment message count
    new_count = group['message_count'] + 1
    if new_count >= group['character_time']:
        # It's time to send a character
        send_character_to_group(group_id)
        new_count = 0  # Reset count

    # Update message count in database
    group_collection.update_one(
        {'id': group_id},
        {'$set': {'message_count': new_count}}
    )



@app.on_message(filters.command(["charatime"], COMMAND_HANDLER)& filters.group)
async def charatime_handler(_, message):
    if message.from_user.id in sudo_users:
        msg = message.text.split(' ')
        if len(msg) < 2:
            await message.reply_text("Please provide a new character time. Use /charatime new_time")
            return

        new_time = int(msg[1])
        group_id = message.chat.id

        # Update character_time in database
        group_collection.update_one(
            {'id': group_id},
            {'$set': {'character_time': new_time}}
        )
        
        await message.reply_text(f"Character time updated to {new_time}.")
        
def send_character_to_group(group_id):
    group = group_collection.find_one({'id': group_id})
    all_characters = collection.find({})

    if 'sent_characters' not in group:
        # This group doesn't have a sent_characters field yet.
        # Add it with an empty list as its value.
        group['sent_characters'] = []
        group_collection.update_one(
            {'id': group_id},
            {'$set': {'sent_characters': []}}
        )

    for character in all_characters:
        if character['id'] not in group['sent_characters']:
            # This character has not been sent to this group yet.
            # Send the character and add its ID to the sent_characters list.
            send_character(character, group_id)
            group_collection.update_one(
                {'id': group_id},
                {'$push': {'sent_characters': character['id']}}
            )
            break
    else:
        # All characters have been sent to this group.
        # Clear the sent_characters list and start over.
        group_collection.update_one(
            {'id': group_id},
            {'$set': {'sent_characters': []}}
        )
        send_character_to_group(group_id)


app.run()

