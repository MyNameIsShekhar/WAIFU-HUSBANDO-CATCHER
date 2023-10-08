from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.error import BadRequest
import random
from telegram.ext import Updater

# List of dictionaries with image links and their names
characters = [
    {"name": "Naruto", "image_url": "https://graph.org/file/9d78c4029a5d0aea6e7d0.jpg", "options": ["Rendi", "amedni", "bkl", "bsdk"]},
    {"name": "Hinata", "image_url": "https://graph.org/file/314324a8e1831137c8f94.jpg", "options": ["gandu", "choda", "moda", "lofa"]},
    # Add more characters as needed
]

# Dictionary to keep track of user attempts
user_attempts = {}

def random(update: Update, context: CallbackContext) -> None:
    # Select a random character
    correct_character = random.choice(characters)
    
    # Create a list of options including the correct one
    options = correct_character["options"].copy()
    options.append(correct_character["name"])
    
    # Shuffle the options to randomize the correct answer's position
    random.shuffle(options)
    
    # Create an inline keyboard with the character names as buttons
    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in options]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the question message with the inline keyboard
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=correct_character["image_url"], caption="Choose Correct Name Of The Character", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    
    # Check if the user has already attempted to answer
    if query.from_user.id in user_attempts and user_attempts[query.from_user.id]:
        query.answer("You've already tried", show_alert=True)
        return
    
    # Check if the selected option is correct
    for character in characters:
        if character["name"] == query.data:
            try:
                query.edit_message_text(text=f"Correct! The character is {query.data}. Well done {query.from_user.first_name}!")
                user_attempts[query.from_user.id] = True
            except BadRequest:
                pass
            return
    
    # If the selected option is incorrect
    query.answer("You're wrong", show_alert=True)
    user_attempts[query.from_user.id] = True

def main() -> None:
    updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('random', random))
    
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

if __name__ == '__main__':
    main()
