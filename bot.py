import asyncio
from pyrogram import Client, filters
from pymongo import MongoClient
import urllib.request

sudo_users = [565452393, 6194728132, 6404226395] 

client = MongoClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')

db = client['lmaoooo']
collection = db['collectionname']


api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6656458442:AAGJ1nKC2qil9SMU3NbElluHSmHJrN8oZsg'

app = Client("my_account", api_id=api_id, api_hash=api_hash, bot_token=bot_token)



@app.on_message(filters.command("upload"))
async def upload(client, message):
    # Check if user is a sudo user
    if int(message.from_user.id) not in sudo_users:
        await message.reply_text('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = message.command[1:]
        if len(args) != 3:
            await message.reply_text('Incorrect format. Please use: /upload img_url Character-Name Anime-Name')
            return

        # Replace '-' with ' ' in character name and convert to title case
        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()

        # Check if image URL is valid
        try:
            urllib.request.urlopen(args[0])
        except:
            await message.reply_text('Invalid image URL.')
            return

        # Generate ID
        id = str(get_next_sequence_number('character_id')).zfill(4)

        # Insert new character
        character = {
            'img_url': args[0],
            'name': character_name,
            'anime': anime,
            'id': id
        }
        
        # Send message to channel
        sent_message = await client.send_photo(
            chat_id='-1001670772912',
            photo=args[0],
            caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n<b>ID:</b> {id}\nAdded by <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>',
            parse_mode='HTML'
        )

        # Save message_id to character
        character['message_id'] = sent_message.message_id
        collection.insert_one(character)

        await message.reply_text('Successfully uploaded.')
    except Exception as e:
        await message.reply_text('Unsuccessfully uploaded.')

@app.on_message(filters.command("delete"))
async def delete(client, message):
    # Check if user is a sudo user
    if str(message.from_user.id) not in sudo_users:
        await message.reply_text('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = message.command[1:]
        if len(args) != 1:
            await message.reply_text('Incorrect format. Please use: /delete ID')
            return

        # Delete character with given ID
        character = collection.find_one_and_delete({'id': args[0]})

        if character:
            # Delete message from channel
            await client.delete_messages(chat_id='-1001670772912', message_ids=character['message_id'])
            await message.reply_text('Successfully deleted.')
        else:
            await message.reply_text('No character found with given ID.')
    except Exception as e:
        await message.reply_text('Failed to delete character.')

app.run()
