import asyncio
import urllib.request
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from aiogram import Bot, types, Dispatcher, executor
from aiogram.utils import executor
import aiohttp 


shuyaa = Telegraph()
telegraph = shuyaa.create_account(short_name-'shigeoooTheSuperman')

# Connect to MongoDB
client = AsyncIOMotorClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
db = client['Waifus']
collection = db['anime_characters']

# Get the collection for user totals
user_totals_collection = db['user_totals']
user_collection = db["user_collection"]

# List of sudo users
sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651']

# Create a dictionary of locks
locks = {}

bot = Bot(token='6347356084:AAHX7A8aY9fbtgCQ-8R16TRBKkCHtX4bMxA')
dp = Dispatcher(bot)

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





@dp.message_handler(commands=['upload'], content_types=types.ContentTypes.PHOTO)
async def upload(message: types.Message):
    # Check if user is a sudo user
    if str(message.from_user.id) not in sudo_users:
        await message.reply('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = message.get_args().split()
        if len(args) != 2:
            await message.reply('Incorrect format. Please reply to a photo with: /upload Character-Name Anime-Name')
            return

        # Replace '-' with ' ' in character name and convert to title case
        character_name = args[0].replace('-', ' ').title()
        anime = args[1].replace('-', ' ').title()

        # Get the photo file_id from the replied message
        photo_file_id = message.reply_to_message.photo[-1].file_id

        # Download the photo
        photo_file_path = await bot.get_file(photo_file_id)
        photo_bytes = await bot.download_file(photo_file_path.file_path)

        # Save the photo locally temporarily
        with open('temp.jpg', 'wb') as f:
            f.write(photo_bytes)

        # Upload the photo to Telegraph and get the URL
        img_path = upload_file('temp.jpg')[0]
        img_url = f'https://telegra.ph{img_path}'

        # Generate ID
        id = str(await get_next_sequence_number('character_id')).zfill(4)

        # Insert new character
        character = {
            'img_url': img_url,
            'name': character_name,
            'anime': anime,
            'id': id
        }
        
        await collection.insert_one(character)

        await message.reply('Successfully uploaded.')
    except Exception as e:
        await message.reply('Unsuccessfully uploaded.')



@dp.message_handler(commands=['delete'])
async def delete(message: types.Message):
    # Check if user is a sudo user
    if str(message.from_user.id) not in sudo_users:
        await message.reply('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = message.get_args().split()
        if len(args) != 1:
            await message.reply('Incorrect format. Please use: /delete ID')
            return

        # Delete character with given ID
        character = await collection.find_one_and_delete({'id': args[0]})

        if character:
            # Delete message from channel
            await bot.delete_message(chat_id='-1001670772912', message_id=character['message_id'])
            await message.reply('Successfully deleted.')
        else:
            await message.reply('No character found with given ID.')
    except Exception as e:
        await message.reply('Failed to delete character.')

@dp.message_handler(commands=['anime'])
async def anime(message: types.Message):
    try:
        # Get all unique anime names
        anime_names = await collection.distinct('anime')

        # Send message with anime names
        await message.reply('\n'.join(anime_names))
    except Exception as e:
        await message.reply('Failed to fetch anime names.')

if __name__ == '__main__':
    executor.start_polling(dp)
