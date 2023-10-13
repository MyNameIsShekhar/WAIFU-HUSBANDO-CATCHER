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
        
# Dictionary to store message count for each group
# Initialize a dictionary to store message counts for each group

@app.on_message(filters.group)
async def group_message_handler(_, message):
    global group_message_counts

    # Increment the message count for the group
    group_id = message.chat.id
    if group_id not in group_message_counts:
        group_message_counts[group_id] = 0
    group_message_counts[group_id] += 1

    # If the message count reaches 100, send a character and reset the count
    if group_message_counts[group_id] >= 10:
        # Get a list of characters that haven't been sent yet
        sent_characters = group_collection.find_one({'id': group_id})['sent_characters']
        unsent_characters = collection.find({'id': {'$nin': sent_characters}})

        if unsent_characters.count() > 0:
            # Choose a character to send
            character = unsent_characters[0]

            # Add the character to the list of sent characters
            sent_characters.append(character['id'])
            group_collection.update_one({'id': group_id}, {'$set': {'sent_characters': sent_characters}})

            # Send the character
            caption = f"Use /Hunt and write {character['character_name']}.. and add this character in Your Collection.."
            await app.send_photo(group_id, character['img_url'], caption=caption)

        else:
            # If all characters have been sent, reset the list of sent characters and start from the beginning
            group_collection.update_one({'id': group_id}, {'$set': {'sent_characters': []}})

        # Reset the message count
        group_message_counts[group_id] = 0


@app.on_chat_member_updated()
async def chat_member_updated_handler(client, chat_member_updated):
    old = chat_member_updated.old_chat_member
    new = chat_member_updated.new_chat_member

    # Check if the bot was added to the group
    if old.status == "left" and new.status == "member":
        group_id = chat_member_updated.chat.id

        # Check if the group is already in the database
        if not group_collection.find_one({'id': group_id}):
            # If not, create a new entry with an empty sent_characters list
            group_collection.insert_one({'id': group_id, 'sent_characters': []})

app.run()

