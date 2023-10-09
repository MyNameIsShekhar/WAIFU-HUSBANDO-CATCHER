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
    if not guess:
        if chat_id in last_characters:
            update.message.reply_text('Please use the format: /guess Character-Name')
        return

    if guess in last_characters[chat_id]['name'].lower():
        # Check if someone has already guessed correctly
        if chat_id in first_correct_guesses:
            update.message.reply_text(f'Already guessed by <a href="tg://user?id={first_correct_guesses[chat_id]}">user</a>', parse_mode='HTML')
            return

        update.message.reply_text('Correct guess!')
        first_correct_guesses[chat_id] = user_id

        # Get user's collection
        user_collection = db[str(user_id)]

        # Check if character is already in user's collection
        existing_character = user_collection.find_one({'id': last_characters[chat_id]['id']})
        if existing_character:
            # If character is already in collection, increment count
            user_collection.update_one({'id': existing_character['id']}, {'$inc': {'count': 1}})
        else:
            # If character is not in collection, add it with count 1
            character = last_characters[chat_id]
            character['count'] = 1
            user_collection.insert_one(character)

        # Increment total count for this user globally
        user_totals_collection.update_one({'user_id': user_id}, {'$inc': {'total': 1}}, upsert=True)
        
def leaderboard(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    # Get all users in the chat and their total counts from the database 
    leaderboard_data = list(user_totals_collection.find({}))

    leaderboard_data.sort(key=lambda x: x['total'], reverse=True)
    
    top_10_data = leaderboard_data[:10]

    leaderboard_message = '\n'.join([f'{i+1}. <a href="tg://user?id={data["user_id"]}">{data["user_name"]}</a>: {data["total"]}' for i, data in enumerate(top_10_data)])

    update.message.reply_text(leaderboard_message, parse_mode='HTML')

def main() -> None:
    updater = Updater(token='6526883785:AAEAGc396CqAuokk5o237ZP4k6dIhB0d6_k')

    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_counter))
    dispatcher.add_handler(CommandHandler('guess', guess))
    dispatcher.add_handler(CommandHandler('leaderboard', leaderboard))

    updater.start_polling()

if __name__ == '__main__':
    main()
