from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from pymongo import MongoClient
import urllib.request
import random

# Connect to MongoDB
client = MongoClient('mongodb+srv://shuyaaaaa12:NvpoBuRp7MVPcAYA@cluster0.q2yycqx.mongodb.net/')
db = client['Waifusss']
collection = db['anime_characters']

# Get the collection for user totals
user_totals_collection = db['user_totals']

# List of sudo users
sudo_users = ['6404226395']

# Counter for messages in each group
message_counters = {}

# Last sent character in each group
last_characters = {}

# Characters that have been sent in each group
sent_characters = {}

# Keep track of the user who guessed correctly first in each group
first_correct_guesses = {}


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

        # Replace '-' with ' ' in character name
        character_name = args[1].replace('-', ' ')

        # Check if image URL is valid
        try:
            urllib.request.urlopen(args[0])
        except:
            update.message.reply_text('Invalid image URL.')
            return

        # Generate ID
        id = str(collection.count_documents({}) + 1).zfill(4)

        # Insert new character
        character = {
            'img_url': args[0],
            'name': character_name,
            'anime': args[2],
            'id': id
        }
        collection.insert_one(character)
        
        update.message.reply_text('Successfully uploaded.')

        # Send message to channel
        context.bot.send_photo(
            chat_id='-1001670772912',
            photo=args[0],
            caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {args[2]}\n<b>ID:</b> {id}\nAdded by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
            parse_mode='HTML'
        )
    except Exception as e:
        update.message.reply_text('Unsuccessfully uploaded.')


def anime(update: Update, context: CallbackContext) -> None:
    try:
        # Get all unique anime names
        anime_names = collection.distinct('anime')

        # Send message with anime names
        update.message.reply_text('\n'.join(anime_names))
    except Exception as e:
        update.message.reply_text('Failed to fetch anime names.')

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
        result = collection.delete_one({'id': args[0]})

        if result.deleted_count > 0:
            update.message.reply_text('Successfully deleted.')
        else:
            update.message.reply_text('No character found with given ID.')
    except Exception as e:
        update.message.reply_text('Failed to delete character.')

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
    all_characters = list(collection.find({}))

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
    guess = ' '.join(context.args).lower() if context.args else ''
    
    if not guess and chat_id in last_characters:
        # If someone has already guessed correctly
        if chat_id in first_correct_guesses:
            update.message.reply_text(f'Already guessed by <a href="tg://user?id={first_correct_guesses[chat_id]}">{update.effective_user.first_name}</a>', parse_mode='HTML')
            return
        else:
            update.message.reply_text('Your guess is incorrect.')
            return

    elif guess and guess in last_characters[chat_id]['name'].lower():
        # Check if someone has already guessed correctly
        if chat_id in first_correct_guesses:
            update.message.reply_text(f'Already guessed by <a href="tg://user?id={first_correct_guesses[chat_id]}">{update.effective_user.first_name}</a>', parse_mode='HTML')
            return

        update.message.reply_text(f'Correct guess! <a href="tg://user?id={user_id}">{update.effective_user.first_name}</a> guessed it right. The character is {last_characters[chat_id]["name"]} from {last_characters[chat_id]["anime"]}.', parse_mode='HTML')
        first_correct_guesses[chat_id] = user_id

        # Get user's collection
        user_collection = db[str(user_id)]

        # Add character to user's collection with count incrementing each time the same character is guessed correctly.
        existing_character = user_collection.find_one({'id': last_characters[chat_id]['id']})
        
        if existing_character:
            # If character is already in collection, increment count
            user_collection.update_one({'id': existing_character['id']}, {'$inc': {'count': 1}})
        else:
            # If character is not in collection, add it with count 1 and other details like username and first name.
            character = last_characters[chat_id]
            character['count'] = 1
            
            username = update.effective_user.username
            
            if username:
                character['username'] = username
                
            character['first_name'] = update.effective_user.first_name
            
            user_collection.insert_one(character)
    
def main() -> None:
    updater = Updater(token='6526883785:AAEAGc396CqAuokk5o237ZP4k6dIhB0d6_k')

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('upload', upload))
    dispatcher.add_handler(CommandHandler('anime', anime))
    dispatcher.add_handler(CommandHandler('delete', delete))
    dispatcher.add_handler(CommandHandler('total', total))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_counter))
    dispatcher.add_handler(CommandHandler('guess', guess))

    updater.start_polling()

if __name__ == '__main__':
    main()
