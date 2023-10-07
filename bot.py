from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
import random

# Dictionary to store character information
characters = {
    "character1": {
        "image": "https://graph.org/file/60dcb0e5dc76ad24d52b8.jpg", 
        "options": ["Obito", "Madara", "Madara", "Lmao", "Lmaoo"],
        "correct": "Obito"
    },
    "character2": {
        "image": "https://graph.org/file/b942cc9107e5909de5498.jpg", 
        "options": ["Mitsuri", "Rendi", "Rednii", "lkxaa4", "option5"],
        "correct": "Mitsuri"
    },
    # Add more characters as needed
}

# Dictionary to store user attempts
user_attempts = {}

# Counter for group messages
message_counter = 0

def send_character(update: Update, context: CallbackContext) -> None:
    global message_counter
    message_counter += 1

    if message_counter % 20 == 0:
        character = random.choice(list(characters.keys()))
        image_url = characters[character]["image"]
        options = characters[character]["options"]
        
        keyboard = [[InlineKeyboardButton(option, callback_data=character)] for option in options]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url, caption="Choose correct name of the character", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    character = query.data
    user_id = query.from_user.id
    
    if user_id in user_attempts and user_attempts[user_id] == character:
        query.edit_message_text(text="You've already tried this one!")
        return
    
    user_attempts[user_id] = character
    
    if query.message.caption == characters[character]["correct"]:
        # User was correct. Add 5 coins to their total in the database here.
        query.edit_message_text(text=f"Correct! You get 5 coins. Your new total is {new_total}.")
    else:
        query.edit_message_text(text="Sorry, that's not correct.")

def main() -> None:
    updater = Updater("5823371420:AAERluGPDzcPUjQzGnRe9OoBbECe19_JFXk", use_context=True)

    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_character))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
