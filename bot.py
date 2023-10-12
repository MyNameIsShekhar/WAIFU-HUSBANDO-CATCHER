import asyncio
import urllib.request
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from aiogram import Bot, types, Dispatcher, executor

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

@dp.message_handler(commands=['upload'])
async def upload(message: types.Message):
    # Check if user is a sudo user
    if str(message.from_user.id) not in sudo_users:
        await message.reply('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = message.get_args().split()
        if len(args) != 3:
            await message.reply('Incorrect format. Please use: /upload img_url Character-Name Anime-Name')
            return

        # Replace '-' with ' ' in character name and convert to title case
        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()

        # Check if image URL is valid
        try:
            urllib.request.urlopen(args[0])
        except:
            await message.reply('Invalid image URL.')
            return

        # Generate ID
        id = str(await get_next_sequence_number('character_id')).zfill(4)

        # Insert new character
        character = {
            'img_url': args[0],
            'name': character_name,
            'anime': anime,
            'id': id
        }
        
        # Send message to channel
        sent_message = await bot.send_photo(
            chat_id='-1001670772912',
            photo=args[0],
            caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n<b>ID:</b> {id}\nAdded by <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>',
            parse_mode='HTML'
        )

        # Save message_id to character
        character['message_id'] = sent_message.message_id
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
