from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent, InputMediaPhoto
from telegram.ext import InlineQueryHandler,CallbackQueryHandler, ChosenInlineResultHandler
from pymongo import MongoClient, ReturnDocument
import urllib.request
import random
from datetime import datetime, timedelta
from threading import Lock

# Connect to MongoDB
client = MongoClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
db = client['Waifus']
collection = db['anime_characters']

# Get the collection for user totals
user_totals_collection = db['user_totals']
user_collection = db["user_collection"]



# List of sudo users
sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651'  ]


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

def change_time(update: Update, context: CallbackContext) -> None:
    # Check if user is a group admin
    user = update.effective_user
    chat = update.effective_chat

    if chat.get_member(user.id).status not in ('administrator', 'creator'):
        update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = context.args
        if len(args) != 1:
            update.message.reply_text('Incorrect format. Please use: /changetime NUMBER')
            return

        # Check if the provided number is greater than or equal to 100
        new_frequency = int(args[0])
        if new_frequency < 100:
            update.message.reply_text('The message frequency must be greater than or equal to 100.')
            return

        # Change message frequency for this chat in the database
        chat_frequency = user_totals_collection.find_one_and_update(
            {'chat_id': str(chat.id)},
            {'$set': {'message_frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        update.message.reply_text(f'Successfully changed character appearance frequency to every {new_frequency} messages.')
    except Exception as e:
        update.message.reply_text('Failed to change character appearance frequency.')



def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)

    # Get or create a lock for this chat
    if chat_id not in locks:
        locks[chat_id] = Lock()
    lock = locks[chat_id]

    # Use the lock to ensure that only one instance of this function can run at a time for this chat
    with lock:
        # Get message frequency and counter for this chat from the database
        chat_frequency = user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get('message_frequency', 20)
            message_counter = chat_frequency.get('message_counter', 0)
        else:
            # Default to 20 messages if not set
            message_frequency = 20
            message_counter = 0

        # Increment counter for this chat
        message_counter += 1

        # Send image after every message_frequency messages
        if message_counter % message_frequency == 0:
            send_image(update, context)
            # Reset counter for this chat
            message_counter = 0

        # Update counter in the database
        user_totals_collection.update_one(
            {'chat_id': chat_id},
            {'$set': {'message_counter': message_counter}},
            upsert=True
        )



def send_image(update: Update, context: CallbackContext) -> None:
    # Acquire the lock
    
        # Your existing send_image code here

    
    chat_id = update.effective_chat.id

    # Get all characters
    # Change it to this
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

    # If someone has already guessed correctly
    if chat_id in first_correct_guesses:
        update.message.reply_text(f'❌️ Already guessed by Someone..So Try Next Time Bruhh')
        return

    # Check if guess is correct
    guess = ' '.join(context.args).lower() if context.args else ''
    
    if guess and guess in last_characters[chat_id]['name'].lower():
        # Set the flag that someone has guessed correctly
        first_correct_guesses[chat_id] = user_id

        # Add character to user's collection
        user = user_collection.find_one({'id': user_id})
        if user:
            # Update username if it has changed
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user['username']:
                user_collection.update_one({'id': user_id}, {'$set': {'username': update.effective_user.username}})
            # Increment count of character in user's collection
            character_index = next((index for (index, d) in enumerate(user['characters']) if d["id"] == last_characters[chat_id]["id"]), None)
            if character_index is not None:
                # Check if 'count' key exists and increment it, otherwise add it
                if 'count' in user['characters'][character_index]:
                    user['characters'][character_index]['count'] += 1
                else:
                    user['characters'][character_index]['count'] = 1
                user_collection.update_one({'id': user_id}, {'$set': {'characters': user['characters']}})
            else:
                # Add character to user's collection
                last_characters[chat_id]['count'] = 1
                user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
        elif hasattr(update.effective_user, 'username'):
            # Create new user document
            last_characters[chat_id]['count'] = 1
            user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'characters': [last_characters[chat_id]]
            })

        update.message.reply_text(f'Congooo ✅️! <a href="tg://user?id={user_id}">{update.effective_user.first_name}</a> guessed it right. The character is {last_characters[chat_id]["name"]} from {last_characters[chat_id]["anime"]}.', parse_mode='HTML')

    else:
        update.message.reply_text('Incorrect guess. Try again.')





def harrem(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Get the user document
    user = user_collection.find_one({'id': user_id})
    if not user or not user['characters']:
        update.message.reply_text('You have not guessed any characters yet.')
        return

    # Get a random character from the user's collection
    character = random.choice(user['characters'])

    # Get the last 5 characters
    last_characters = user['characters'][-5:]

    # Create the caption
    caption = 'Your latest characters:\n\n'
    for char in last_characters:
        caption += f'{char["name"]} from {char["anime"]}\n'

    # Add the inline keyboard button
    keyboard = [[InlineKeyboardButton('See all waifus (' + str(len(user['characters'])) + ')', switch_inline_query_current_chat=str(user_id))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the character's image with the caption and inline keyboard button
    context.bot.send_photo(
        chat_id=update.effective_chat.id,  # Send in the group where the command was issued
        photo=character['img_url'],
        caption=caption,
        reply_markup=reply_markup
    )

def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query

    # Check if the query is a user id
    if query.isdigit():
        # Find the user in the database
        user = user_collection.find_one({'id': int(query)})

        if user:
            # Create a list of InlineQueryResultPhoto for each character
            results = []
            added_characters = set()
            for character in user['characters']:
                if character['name'] not in added_characters:
                    # Count how many characters from the same anime the user has guessed
                    anime_characters_guessed = sum(c['anime'] == character['anime'] for c in user['characters'])
                    # Count total characters from the same anime
                    total_anime_characters = collection.count_documents({'anime': character['anime']})

                    # Find all users who have this character
                    users_with_character = list(user_collection.find({'characters.id': character['id']}))
                    # Create a list of mentions for each user
                    mentions = [f'<a href="tg://user?id={user["id"]}">{user["username"]}</a>' for user in users_with_character]

                    results.append(
                        InlineQueryResultPhoto(
                            id=character['id'],
                            photo_url=character['img_url'],
                            thumb_url=character['img_url'],
                            caption=f"🔥 <b>Character Name:</b> {character['name']} ×{character.get('count', 0)}\n📺 <b>Anime Name:</b> {character['anime']} ({anime_characters_guessed}/{total_anime_characters})\n👥 <b>Owned by:</b> {', '.join(mentions)}",
                            parse_mode='HTML'
                        )
                    )
                    added_characters.add(character['name'])

            # Answer the inline query
            update.inline_query.answer(results)
        else:
            update.inline_query.answer([])
    else:
        # If no id is given, show all characters from upload database
        all_characters = list(collection.find({}))
        results = [
            InlineQueryResultPhoto(
                id=character['id'],
                photo_url=character['img_url'],
                thumb_url=character['img_url'],
                caption=f"Character Name: {character['name']}\nAnime Name: {character['anime']}",
                parse_mode='HTML'
            )
            for character in all_characters
        ]
        update.inline_query.answer(results)

# Add InlineQueryHandler and ChosenInlineResultHandler to the dispatcher

# Add InlineQueryHandler to the dispatcher
def main() -> None:
    updater = Updater(token='6347356084:AAHX7A8aY9fbtgCQ-8R16TRBKkCHtX4bMxA')

    dispatcher = updater.dispatcher

    
    dispatcher.add_handler(CommandHandler('upload', upload, run_async=True))
    
    dispatcher.add_handler(CommandHandler('delete', delete, run_async=True))
    
    dispatcher.add_handler(CommandHandler('anime', anime, run_async=True))
    dispatcher.add_handler(CommandHandler('total', total, run_async=True))
    dispatcher.add_handler(CommandHandler('changetime', change_time, run_async=True))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_counter, run_async=True))
    dispatcher.add_handler(CommandHandler('guess', guess, run_async=True))
    # Add CommandHandler for /list command to your Updater
    dispatcher.add_handler(CommandHandler('harrem', harrem, run_async=True))
    dispatcher.add_handler(InlineQueryHandler(inlinequery, run_async=True))
    

    updater.start_polling()

if __name__ == '__main__':
    main()
