from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Updater 
from telegram.error import BadRequest
import random

from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb+srv://shuyaaaaa12:NvpoBuRp7MVPcAYA@cluster0.q2yycqx.mongodb.net/")
db = client["Japanese_database"]
collection = db["Japanese_users"]
characters_collection = db["Japanese_characters"]

# Dictionary to keep track of user attempts and message counts
group_data = {}

def count_messages(update: Update, context: CallbackContext) -> None:
    # Increment the message count for the group
    group_id = update.effective_chat.id
    if group_id not in group_data:
        group_data[group_id] = {"message_count": 0, "user_attempts": {}, "character_index": 0}
    group_data[group_id]["message_count"] += 1
    
    # If the message count reaches 20, reset it and ask a question
    if group_data[group_id]["message_count"] >= 20:
        group_data[group_id]["message_count"] = 0
        group_data[group_id]["user_attempts"] = {}
        question(update, context)

def question(update: Update, context: CallbackContext) -> None:
    # Fetch all characters from the database
    characters = list(characters_collection.find())
    
    # Get the group data
    group_id = update.effective_chat.id
    group_data.setdefault(group_id, {"message_count": 0, "user_attempts": {}, "character_index": 0})
    
    # Select the next character
    correct_character = characters[group_data[group_id]["character_index"]]
    
    # Increment the character index for the next question
    group_data[group_id]["character_index"] = (group_data[group_id]["character_index"] + 1) % len(characters)
    
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

def upload(update: Update, context: CallbackContext) -> None:
    # Extract arguments from the command
    args = context.args
    
    if len(args) < 3:
        update.message.reply_text("Please provide an image URL, name and options in the format.. ask @shigeoo")
        return
    
    image_url = args[0]
    name = args[1]
    options = args[2].split(',')
    
    # Insert the new character into the database
    try:
        characters_collection.insert_one({"name": name, "image_url": image_url, "options": options})
        update.message.reply_text("Successfully uploaded.")
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

def delete(update: Update, context: CallbackContext) -> None:
    # Extract arguments from the command
    args = context.args
    
    if len(args) != 1:
        update.message.reply_text("Please provide a name in the format: /delete <name>")
        return
    
    name = args[0]
    
    # Delete the character from the database
    try:
        characters_collection.delete_one({"name": name})
        if characters_collection.count_documents({"name": name}) == 0:
            update.message.reply_text("Successfully deleted.")
        else:
            update.message.reply_text("Error: Character not found.")
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

def main() -> None:
    updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command, count_messages))
    
    dispatcher.add_handler(CallbackQueryHandler(button))
    
    dispatcher.add_handler(CommandHandler("upload", upload))
    
    dispatcher.add_handler(CommandHandler("delete", delete))

    updater.start_polling()

if __name__ == '__main__':
    main()
