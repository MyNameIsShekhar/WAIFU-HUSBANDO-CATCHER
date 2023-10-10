from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent
from telegram.ext import InlineQueryHandler,CallbackQueryHandler
from pymongo import MongoClient, ReturnDocument
import urllib.request
import random

# Connect to MongoDB
client = MongoClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
db = client['Waifus']
collection = db['anime_characters']

# Get the collection for user totals
user_totals_collection = db['user_totals']
user_collection = db["user_collection"]


# List of sudo users
sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651'  ]

# Counter for messages in each group
message_counters = {}

# Last sent character in each group
last_characters = {}

# Characters that have been sent in each group
sent_characters = {}

# Keep track of the user who guessed correctly first in each group
first_correct_guesses = {}




def get_next_sequence_number(sequence_name):
    # Get a handle to the sequence collection
    sequence_collection = db.sequences

    # Use find_one_and_update to atomically increment the sequence number
    sequence_document = sequence_collection.find_one_and_update(
        {'_id': sequence_name}, 
        {'$inc': {'sequence_value': 1}}, 
        return_document=ReturnDocument.AFTER
    )

    # If this sequence doesn't exist yet, create it
    if not sequence_document:
        sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0

    return sequence_document['sequence_value']

def upload(update: Update, context: CallbackContext) -> None:
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
        id = str(get_next_sequence_number('character_id')).zfill(4)

        # Insert new character
        character = {
            'img_url': args[0],
            'name': character_name,
            'anime': anime,
            'id': id
        }
        
        # Send message to channel
        message = context.bot.send_photo(
            chat_id='-1001670772912',
            photo=args[0],
            caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n<b>ID:</b> {id}\nAdded by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
            parse_mode='HTML'
        )

        # Save message_id to character
        character['message_id'] = message.message_id
        collection.insert_one(character)

        update.message.reply_text('Successfully uploaded.')
    except Exception as e:
        update.message.reply_text('Unsuccessfully uploaded.')

def delete(update: Update, context: CallbackContext) -> None:
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
        character = collection.find_one_and_delete({'id': args[0]})

        if character:
            # Delete message from channel
            context.bot.delete_message(chat_id='-1001670772912', message_id=character['message_id'])
            update.message.reply_text('Successfully deleted.')
        else:
            update.message.reply_text('No character found with given ID.')
    except Exception as e:
        update.message.reply_text('Failed to delete character.')


def anime(update: Update, context: CallbackContext) -> None:
    try:
        # Get all unique anime names
        anime_names = collection.distinct('anime')

        # Send message with anime names
        update.message.reply_text('\n'.join(anime_names))
    except Exception as e:
        update.message.reply_text('Failed to fetch anime names.')


def total(update: Update, context: CallbackContext) -> None:
    try:
        # Extract arguments
        args = context.args
        if len(args) != 1:
            update.message.reply_text('Incorrect format. Please use: /total Anime-Name')
            return

        # Replace '-' with ' ' in anime name
        anime_name = args[0].replace('-', ' ')

        # Get all characters of the given anime
        characters = collection.find({'anime': anime_name})

        # Create a list of character names and IDs
        character_list = [f'Character Name: {character["name"]}\nID: {character["id"]}' for character in characters]

        # Send message with character names and IDs
        update.message.reply_text('\n\n'.join(character_list))
    except Exception as e:
        update.message.reply_text('Failed to fetch characters.')




def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    # Increment counter for this chat
    if chat_id not in message_counters:
        message_counters[chat_id] = 0
    message_counters[chat_id] += 1

    # Send image after every 20 messages
    if message_counters[chat_id] % 20 == 0:
        send_image(update, context)

def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    # Get all characters
    # Change it to this
    all_characters = [character for character in collection.find({})]
    # Initialize sent characters list for this chat if it doesn't exist
    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    # Reset sent characters list if all characters have been sent
    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    # Select a random character that hasn't been sent yet
    character = random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])

    # Add character to sent characters list and set as last sent character
    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    # Reset first correct guess when a new character is sent
    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    # Send image with caption
    context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption="Use /Guess Command And.. Guess This Character Name.."
    )
def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if a character has been sent in this chat yet
    if chat_id not in last_characters:
        return

    # Check if guess is correct
    guess = ' '.join(context.args).title() if context.args else ''
    
    if chat_id in last_characters:
        # If someone has already guessed correctly
        if chat_id in first_correct_guesses:
            update.message.reply_text(f'❌️ Already guessed by Someone..So Try Next Time Bruhh')
            return

        elif guess and guess in last_characters[chat_id]['name'].title():
            # Add character to user's collection
            user = user_collection.find_one({'id': user_id})
            if user:
                # Update username if it has changed
                if 'username' in update.effective_user and update.effective_user.username != user['username']:
                    user_collection.update_one({'id': user_id}, {'$set': {'username': update.effective_user.username}})
                # Add character to user's collection
                user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
            elif 'username' in update.effective_user:
                # Create new user document
                user_collection.insert_one({
                    'id': user_id,
                    'username': update.effective_user.username,
                     'first_name': update.effective_user.first_name,
                
                    'characters': [last_characters[chat_id]]
                })

            update.message.reply_text(f'Congooo ✅️! <a href="tg://user?id={user_id}">{update.effective_user.first_name}</a> guessed it right. The character is {last_characters[chat_id]["name"]} from {last_characters[chat_id]["anime"]}.', parse_mode='HTML')
            
        else:
            
            update.message.reply_text('❌️ Try Again....')

def collection(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Get user document
    user = user_collection.find_one({'id': user_id})

    if not user or 'characters' not in user or not user['characters']:
        update.message.reply_text('You have not guessed any characters correctly yet.')
        return

    # Create a list of character names and IDs
    shuyaa = [f'Character Name: {character["name"]}\nID: {character["id"]}' for character in user['characters']]

    # Send message with character names and IDs
    update.message.reply_text('\n\n'.join (shuyaa))


# Connect to MongoDB

# Create a new collection for user collections




def main() -> None:
    updater = Updater(token='6347356084:AAHX7A8aY9fbtgCQ-8R16TRBKkCHtX4bMxA')

    dispatcher = updater.dispatcher

    
    dispatcher.add_handler(CommandHandler('anime', anime))
    
    dispatcher.add_handler(CommandHandler('upload', upload))
    
    dispatcher.add_handler(CommandHandler('delete', delete))
    dispatcher.add_handler(CommandHandler('total', total))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_counter))
    dispatcher.add_handler(CommandHandler('guess', guess))
    # Add CommandHandler for /list command to your Updater
    dispatcher.add_handler(CommandHandler('collection', collection))



    updater.start_polling()

if __name__ == '__main__':
    main()
