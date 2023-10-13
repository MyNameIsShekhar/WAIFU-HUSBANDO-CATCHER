from pyrogram import Client, filters
from pymongo import MongoClient
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

sudo_users = [6404226395]  # Add more sudo user IDs to this list if needed

@app.on_message(filters.command("upload"))
async def upload_handler(_, message):
    # Check if the user is a sudo user
    if message.from_user.id in sudo_users:
        msg = message.text.split(' ')
        if len(msg) == 4:
            img_url, anime_name, character_name = msg[1], msg[2].replace('-', ' '), msg[3].replace('-', ' ')
            # Check if the URL is valid
            if re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', img_url):
                # Insert into MongoDB
                character_doc = {
                    "anime_name": anime_name,
                    "character_name": character_name,
                    "img_url": img_url,
                    "added_by": message.from_user.id
                }
                collection.insert_one(character_doc)
                await message.reply_text("Successfully uploaded.")
                
                # Download image
                response = requests.get(img_url)
                file_name = os.path.join('/tmp', 'image.jpg')
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                
                # Send to channel
                channel_id = -1001670772912  # Replace with your channel ID
                caption = f'{message.from_user.mention} added a new character:\n\n' \
                          f'Anime: {anime_name}\n' \
                          f'Character: {character_name}'
                await app.send_photo(channel_id, file_name, caption=caption)
                
                # Delete image file
                os.remove(file_name)
            else:
                await message.reply_text("Invalid image URL.")
        else:
            await message.reply_text("Incorrect format. Use /upload img_url anime-name character-name")
    else:
        await message.reply_text("Only sudo users can use this command.")

def main():
    asyncio.run(app.run())

if __name__ == "__main__":
    main()
