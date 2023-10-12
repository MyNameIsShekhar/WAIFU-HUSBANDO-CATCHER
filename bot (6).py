from telethon import TelegramClient, events
from telegraph import Telegraph, upload_file
import os
import requests

api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6347356084:AAHX7A8aY9fbtgCQ-8R16TRBKkCHtX4bMxA'
dp = Dispatcher(bot)

telegraph = Telegraph()
telegraph.create_account(short_name='anime')

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)


async def get_next_sequence_number(sequence_name):
    # Get a handle to the sequence collection
    sequence_collection = db.sequences

    # Use find_one_and_update to atomically increment the sequence number
    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name}, 
        {'$inc': {'sequence_value': 1}}, 
        return_document=ReturnDocument.AFTER
    )

    # If this sequence doesn't exist yet, create it
    if not sequence_document:
        await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0

    return sequence_document['sequence_value']

@client.on(events.NewMessage(pattern='/upload'))
async def upload(event):
    # Check if user is a sudo user
    if str(event.message.sender_id) not in sudo_users:
        await event.reply('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = event.message.text.split()[1:]
        if len(args) != 2:
            await event.reply('Incorrect format. Please reply to an image with: /upload Character-Name Anime-Name')
            return

        # Check if replied to a photo
        if not event.message.is_reply or 'photo' not in event.message.reply_to_message.media:
            await event.reply('Please reply to a photo.')
            return

        # Replace '-' with ' ' in character name and convert to title case
        character_name = args[0].replace('-', ' ').title()
        anime = args[1].replace('-', ' ').title()

        # Download image
        photo_path = await event.message.reply_to_message.download_media()

        # Upload image to telegraph
        response = upload_file(photo_path)

        # Delete downloaded image
        os.remove(photo_path)

        # Generate ID
        id = str(await get_next_sequence_number('character_id')).zfill(4)

        # Insert new character
        character = {
            'img_url': 'https://telegra.ph' + response[0],
            'name': character_name,
            'anime': anime,
            'id': id
        }

        collection.insert_one(character)

        # Send image with caption to group
        await client.send_file(
            'your_group_id',
            file=character['img_url'],
            caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n<b>ID:</b> {id}',
            parse_mode='html'
        )

        await event.reply('Successfully uploaded.')
    except Exception as e:
        await event.reply('Unsuccessfully uploaded.')

client.run_until_disconnected()
