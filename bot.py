from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Updater 
from telegram.error import BadRequest
import random

from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb+srv://shuyaaaaa12:NvpoBuRp7MVPcAYA@cluster0.q2yycqx.mongodb.net/")
db = client["Japanese_database"]
collection = db["Japanesewoedss"]

# List of dictionaries with image links and their names
characters = [
    {"name": "Idiot", "image_url": "https://graph.org/file/428c2ab890a2bc4caa4c3.jpg", "options": ["Goodbye", "Cry", "Handsome", "intelligent"]},
    {"name": "Good Morning", "image_url": "https://te.legra.ph/file/687db2df2db365151e289.jpg", "options": ["goodnight", "LoveYou", "GoodBye", "HateYou"]},
    # Add more characters as needed
]
# Dictionary to keep track of user attempts and message counts
group_data = {}

def count_messages(update: Update, context: CallbackContext) -> None:
    # Increment the message count for the group
    group_id = update.effective_chat.id
    if group_id not in group_data:
        group_data[group_id] = {"message_count": 0, "user_attempts": {}}
    group_data[group_id]["message_count"] += 1
    
    # If the message count reaches 20, reset it and ask a question
    if group_data[group_id]["message_count"] >= 20:
        group_data[group_id]["message_count"] = 0
        group_data[group_id]["user_attempts"] = {}
        question(update, context)

def question(update: Update, context: CallbackContext) -> None:
    # Select a random character
    correct_character = random.choice(characters)
    
    # Create a list of options including the correct one
    options = correct_character["options"].copy()
    options.append(correct_character["name"])
    
    # Shuffle the options to randomize the correct answer's position
    random.shuffle(options)
    
    # Create an inline keyboard with the character names as buttons
    keyboard = [
        [InlineKeyboardButton(options[i], callback_data=options[i]) for i in range(3)],  # First row with 3 buttons
        [InlineKeyboardButton(options[i], callback_data=options[i]) for i in range(3, 5)]  # Second row with 2 buttons
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the question message with the inline keyboard
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=correct_character["image_url"], caption="Choose Correct Name Of The Character", reply_markup=reply_markup)
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    
    # Check if the user has already attempted to answer
    group_id = query.message.chat_id
    user_id = query.from_user.id
    
    if user_id in group_data[group_id]["user_attempts"] and group_data[group_id]["user_attempts"][user_id]:
        query.answer("You've already tried", show_alert=True)
        return
    
    # Check if the selected option is correct
    for character in characters:
        if character["name"] == query.data:
            try:
                # Delete the original message
                context.bot.delete_message(chat_id=group_id, message_id=query.message.message_id)
                
                # Send a new message
                context.bot.send_message(chat_id=group_id, text=f"Correct! The character is {query.data}. Well done {query.from_user.first_name}!")
                
                group_data[group_id]["user_attempts"][user_id] = True
                
                # Give the user 5 coins in this group and globally
                
                # Prepare the update document for MongoDB
                update_doc_group = {"$set": {"first_name": query.from_user.first_name}, "$inc": {"coins": 5}}
                update_doc_global = {"$set": {"first_name": query.from_user.first_name}, "$inc": {"global_coins": 5}}
                if query.from_user.username is not None:
                    
                
                    update_doc_group["$set"]["username"] = query.from_user.username
                    update_doc_global["$set"]["username"] = query.from_user.username
                
                # Update the user's coins in this group
                collection.update_one({"group_id": group_id, "user_id": user_id}, update_doc_group, upsert=True)
                
                # Update the user's global coins
                collection.update_one({"user_id": user_id}, update_doc_global, upsert=True)
            except BadRequest:
                pass
            return
    
    # If the selected option is incorrect
    query.answer("You're wrong", show_alert=True)
    group_data[group_id]["user_attempts"][user_id] = True

def main() -> None:
    updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command, count_messages))
    
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

if __name__ == '__main__':
    main()
