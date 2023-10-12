import asyncio
import urllib.request
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler, ChosenInlineResultHandler

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
# Counter for messages in each group
message_counters = {}
spam_counters = {}
# Last sent character in each group
last_characters = {}

# Characters that have been sent in each group
sent_characters = {}

# Keep track of the user who guessed correctly first in each group
first_correct_guesses = {}

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

async def upload(update: Update, context: CallbackContext) -> None:
    # Check if user is a sudo user
    if str(update.effective_user.id) not in sudo_users:
        update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = context.args
        if len(args) != 3:
            update.message.reply_text('Incorrect format. Please use: /upload img_url Character-Name Anime-Name')
            return

        # Replace '-' with ' ' in character name and convert to title case
        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()

        # Check if image URL is valid
        try:
            urllib.request.urlopen(args[0])
        except:
            update.message.reply_text('Invalid image URL.')
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
        message = await context.bot.send_photo(
            chat_id='-1001670772912',
            photo=args[0],
            caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n<b>ID:</b> {id}\nAdded by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
            parse_mode='HTML'
        )

        # Save message_id to character
        character['message_id'] = message.message_id
        await collection.insert_one(character)

        update.message.reply_text('Successfully uploaded.')
    except Exception as e:
        update.message.reply_text('Unsuccessfully uploaded.')

async def delete(update: Update, context: CallbackContext) -> None:
    # Check if user is a sudo user
    if str(update.effective_user.id) not in sudo_users:
        update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = context.args
        if len(args) != 1:
            update.message.reply_text('Incorrect format. Please use: /delete ID')
            return

        # Delete character with given ID
        character = await collection.find_one_and_delete({'id': args[0]})

        if character:
            # Delete message from channel
            await context.bot.delete_message(chat_id='-1001670772912', message_id=character['message_id'])
            update.message.reply_text('Successfully deleted.')
        else:
            update.message.reply_text('No character found with given ID.')
    except Exception as e:
        update.message.reply_text('Failed to delete character.')

async def anime(update: Update, context: CallbackContext) -> None:
    try:
        # Get all unique anime names
        anime_names = await collection.distinct('anime')

        # Send message with anime names
        update.message.reply_text('\n'.join(anime_names))
    except Exception as e:
        update.message.reply_text('Failed to fetch anime names.')


async def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("upload", upload))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(CommandHandler("anime", anime))


    # Add command handlers
    #dp.add_handler(CommandHandler("changetime", change_time))
    #dp.add_handler(CommandHandler("message_counter", message_counter))
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

# Run the main function
if __name__ == '__main__':
    asyncio.run(main())
