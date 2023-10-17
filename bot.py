from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent, InputMediaPhoto, InlineQueryResultArticle
from telegram.ext import InlineQueryHandler,CallbackQueryHandler, ChosenInlineResultHandler
from pymongo import MongoClient, ReturnDocument
import urllib.request
import random
from threading import Lock
import time 
#Connect to MongoDB
client = MongoClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
db = client['Waifus_lol']
collection = db['anime_characters_lol']

# Get the collection for user totals
user_totals_collection = db['user_totals_lol']
user_collection = db["user_collection_lol"]



# List of sudo users
sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651', '5813998595', '5813403535', '6393627898' ]


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




def start(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type == 'private':
        url = 'https://graph.org/file/6c27800378df0aedb1596.jpg'
        caption = "𝙃𝙚𝙡𝙡𝙤 𝙄𝙩𝙨 𝙂𝙪𝙚𝙨𝙨 '𝙀𝙢 𝙖𝙡𝙡 𝘾𝙝𝙖𝙧𝙖𝙘𝙩𝙚𝙧 𝘽𝙤𝙩.. 𝙄𝙩𝙨 𝙅𝙪𝙨𝙩 𝘽𝙚𝙩𝙖 𝙏𝙚𝙨𝙩𝙞𝙣𝙜 𝙑𝙚𝙧𝙨𝙞𝙤𝙣... 𝙎𝙤 𝙞𝙛 𝙐 𝙒𝙖𝙣𝙣 𝘼𝙙𝙙 𝙩𝙝𝙞𝙨 𝘽𝙤𝙩 𝙞𝙣 𝙔𝙤𝙪'𝙧𝙚 𝙔𝙤𝙪 𝘾𝙖𝙣 𝘼𝙙𝙙..."
        keyboard = [[InlineKeyboardButton("add me in You're group", url='https://t.me/Collect_emAll_Bot?startgroup=_')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=url, caption=caption, reply_markup=reply_markup)

def ping(update: Update, context: CallbackContext) -> None:
    start_time = time.time()
    message = update.message.reply_text('Pong!')
    end_time = time.time()
    elapsed_time = round((end_time - start_time) * 1000, 3)
    message.edit_text(f'Pong! {elapsed_time}ms')

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
            chat_id='-1001915956222',
            photo=args[0],
            caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n<b>ID:</b> {id}\nAdded by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
            parse_mode='HTML'
        )

        # Save message_id to character
        character['message_id'] = message.message_id
        collection.insert_one(character)

        update.message.reply_text('Done...@characters_database.')
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
            context.bot.delete_message(chat_id='-1001915956222', message_id=character['message_id'])
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
            message_frequency = chat_frequency.get('message_frequency', 100)
            message_counter = chat_frequency.get('message_counter', 0)
        else:
            # Default to 20 messages if not set
            message_frequency = 100
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
    query = update.inline_query.query     

    if query.isdigit():
        user = user_collection.find_one({'id': int(query)})

        if user:
            results = []
            added_characters = set()
            for character in user['characters']:
                if character['name'] not in added_characters:
                    anime_characters_guessed = sum(c['anime'] == character['anime'] for c in user['characters'])
                    total_anime_characters = collection.count_documents({'anime': character['anime']})

                    results.append(
                        InlineQueryResultPhoto(
                            id=character['id'],
                            photo_url=character['img_url'],
                            thumb_url=character['img_url'],
                            caption=f"🌻 <b><a href='tg://user?id={user['id']}'>{user.get('username', user['id'])}</a></b>'s Character\n\n<b>Name:</b> {character['name']} " + (f"(x{character.get('count', 1)})" if character.get('count', 1) > 1 else "") + f"\n<b>Anime:</b> {character['anime']} ({anime_characters_guessed}/{total_anime_characters})\n\n🆔: {character['id']}",
                            parse_mode='HTML'
                        )
                    )
                    added_characters.add(character['name'])

            update.inline_query.answer(results)
        else:
            update.inline_query.answer([InlineQueryResultArticle(
                id='notfound', 
                title="User not found", 
                input_message_content=InputTextMessageContent("User not found")
            )])
    else:
        all_characters = list(collection.find({}))
        results = []
        for character in all_characters:
            users_with_character = list(user_collection.find({'characters.id': character['id']}))
            total_guesses = sum(character.get("count", 1) for user in users_with_character)

            results.append(
                InlineQueryResultPhoto(
                    id=character['id'],
                    photo_url=character['img_url'],
                    thumb_url=character['img_url'],
                    caption=f"<b>Look at this character!</b>\n\n⟹ <b>{character['name']}</b>\n⟹ <b>{character['anime']}</b>\n🆔: {character['id']}\n\n<b>Guessed {total_guesses} times In Globally</b>",
                    parse_mode='HTML'
                )
            )
        update.inline_query.answer(results)
def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Check if an ID was provided
    if not context.args:
        update.message.reply_text('Please provide a character ID.')
        return

    character_id = context.args[0]

    # Get the user document
    user = user_collection.find_one({'id': user_id})
    if not user:
        update.message.reply_text('You have not guessed any characters yet.')
        return

    # Check if the character is in the user's collection
    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        update.message.reply_text('This character is not in your collection.')
        return

    # Add character to user's favorites
    if 'favorites' in user:
        if character_id in user['favorites']:
            update.message.reply_text('This character is already in your favorites.')
            return
        else:
            user['favorites'].append(character_id)
    else:
        user['favorites'] = [character_id]

    # Update user document
    user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})

    update.message.reply_text(f'Character {character["name"]} has been added to your favorites.')


PAGE_SIZE = 10

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def myfav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    page = int(context.args[0]) if context.args else 0

    # Get the user document
    user = user_collection.find_one({'id': user_id})
    if not user or 'favorites' not in user or not user['favorites']:
        update.message.reply_text('You have not favorited any characters yet.')
        return

    # Get the favorite characters for this page
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    favorites = user['favorites'][start:end]

    # Build the message text and inline keyboard buttons
    text = ''
    buttons = []
    for character in favorites:
        anime_characters_guessed = sum(c['anime'] == character['anime'] for c in user['characters'])
        total_anime_characters = collection.count_documents({'anime': character['anime']})

        text += f"\n\n<b>Name:</b> {character['name']}\n<b>Anime:</b> {character['anime']} ({anime_characters_guessed}/{total_anime_characters})\n<b>Guessed:</b> {character.get('count', 1)} times\n<b>ID:</b> {character['id']}"

        buttons.append(InlineKeyboardButton(character['name'], switch_inline_query_current_chat=str(character['id'])))

    # Add navigation buttons
    footer_buttons = []
    if page > 0:
        footer_buttons.append(InlineKeyboardButton('Prev', callback_data=f'myfav {page - 1}'))
    if end < len(user['favorites']):
        footer_buttons.append(InlineKeyboardButton('Next', callback_data=f'myfav {page + 1}'))

    reply_markup = InlineKeyboardMarkup(build_menu(buttons, n_cols=2, footer_buttons=footer_buttons))

    # Send the message
    update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

# Add InlineQueryHandler to the dispatcher
def main() -> None:
    updater = Updater(token='6420751168:AAEtf-OyEYLLTZM2c4LrhIroXPfvsW7KlM8')

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start, run_async=True))
    
    dispatcher.add_handler(CommandHandler('upload', upload, run_async=True))
    
    dispatcher.add_handler(CommandHandler('delete', delete, run_async=True))
    
    dispatcher.add_handler(CommandHandler('anime', anime, run_async=True))
    dispatcher.add_handler(CommandHandler('total', total, run_async=True))
    dispatcher.add_handler(CommandHandler('changetime', change_time, run_async=True))
    dispatcher.add_handler(CommandHandler('ping', ping, run_async=True))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_counter, run_async=True))
    dispatcher.add_handler(CommandHandler('guess', guess, run_async=True))
    # Add CommandHandler for /list command to your Updater
    dispatcher.add_handler(CommandHandler('harrem', harrem, run_async=True))
    dispatcher.add_handler(InlineQueryHandler(inlinequery, run_async=True))
    dispatcher.add_handler(CommandHandler('fav', fav, run_async=True))
    dispatcher.add_handler(CommandHandler('myfav', myfav, run_async=True))
    
    

    updater.start_polling()

if __name__ == '__main__':
    main()
