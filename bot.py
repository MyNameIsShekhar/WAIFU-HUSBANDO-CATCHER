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
current_character_index = 0

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

# Create a variable to keep track of the current character index


def question(update: Update, context: CallbackContext) -> None:
    global current_character_index  # Use the global variable

    # Select the character at the current index
    correct_character = characters[current_character_index]

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
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=correct_character["image_url"], caption=f"<b>🖼 Cʜᴏᴏsᴇ Tʜᴇ Cᴏʀʀᴇᴄᴛ Mᴇᴀɴɪɴɢ Oғ Tʜɪs Jᴀᴘɴᴇsᴇ Wᴏʀᴅ ɪɴ Eɴɢʟɪsʜ.. Aɴᴅ Gᴇᴛ Pᴏɪɴᴛs..</b>", parse_mode='HTML', reply_markup=reply_markup)

    # Increment the index and reset it to 0 if it's out of bounds
    current_character_index += 1
    if current_character_index >= len(characters):
        current_character_index = 0
        
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    
    # Check if the user has already attempted to answer
    group_id = query.message.chat_id
    user_id = query.from_user.id

    # Initialize group_data for this group and user if it doesn't exist
    if group_id not in group_data:
        group_data[group_id] = {"message_count": 0, "user_attempts": {}}
    if user_id not in group_data[group_id]["user_attempts"]:
        group_data[group_id]["user_attempts"][user_id] = False

    # Get the character names
    character_names = [character["name"] for character in characters]

    # Only check user_attempts for character questions
    if query.data in character_names and group_data[group_id]["user_attempts"][user_id]:
        query.answer("You've already tried", show_alert=True)
        return
    
    # Check if the selected option is correct
    for character in characters:
        if character["name"] == query.data:
            try:
                # Delete the original message
                context.bot.delete_message(chat_id=group_id, message_id=query.message.message_id)
                
                # Prepare the update document for MongoDB
                update_doc_group = {"$set": {"first_name": query.from_user.first_name}, "$inc": {"points": 5}}
                update_doc_global = {"$set": {"first_name": query.from_user.first_name}, "$inc": {"global_points": 5}}
                if query.from_user.username is not None:
                    update_doc_group["$set"]["username"] = query.from_user.username
                    update_doc_global["$set"]["username"] = query.from_user.username
                
                # Update the user's coins in this group
                collection.update_one({"group_id": group_id, "user_id": user_id}, update_doc_group, upsert=True)
                
                # Update the user's global coins
                collection.update_one({"user_id": user_id}, update_doc_global, upsert=True)
                
                # Fetch the updated points from MongoDB
                group_points_doc = collection.find_one({"group_id": group_id, "user_id": user_id})
                global_points_doc = collection.find_one({"user_id": user_id})
                
                group_points = group_points_doc.get("points", 0) if group_points_doc else 0
                global_points = global_points_doc.get("global_points", 0) if global_points_doc else 0
                
                # Send a new message with HTML formatting
                context.bot.send_message(chat_id=group_id, text=f"<b>The Meaning is {query.data} ...\n{query.from_user.first_name} Answers/Guessed First.. \n{query.from_user.first_name} Wins 5 Ponits 🏆\nTotal Group Points: {group_points}\nTotal Global Points: {global_points}</b>", parse_mode='HTML')
                
                group_data[group_id]["user_attempts"][user_id] = True
                
            except BadRequest:
                pass
            return
    
    # If the selected option is incorrect
    query.answer("You're wrong", show_alert=True)
    group_data[group_id]["user_attempts"][user_id] = True

def leaderboard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # Create an inline keyboard with the "Group" and "Global" buttons
    keyboard = [
        [InlineKeyboardButton("Group", callback_data="group"),
         InlineKeyboardButton("Global", callback_data="global")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline keyboard
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose a leaderboard:", reply_markup=reply_markup)


def leaderboard_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    if data in ["group", "global"]:
        # Fetch the top 10 users from MongoDB
        sort_field = "points" if data == "group" else "global_points"
        top_users = collection.find().sort(sort_field, -1).limit(10)

        # Format the leaderboard message
        message = f"{data.capitalize()} Leaderboard:\n\n"
        for i, user in enumerate(top_users, start=1):
            first_name = user["first_name"]
            if len(first_name) > 7:
                first_name = first_name[:7] + "..."
            username = user.get("username")
            points = user[sort_field]
            if username:
                message += f"{i}. {first_name}: {points} points\n"
            else:
                message += f"{i}. {first_name}: {points} points\n"

        # Add the current user's total points to the end of the message
        current_user_points_doc = collection.find_one({"user_id": query.from_user.id})
        current_user_points = current_user_points_doc.get(sort_field, 0) if current_user_points_doc else 0
        message += f"\nYour total {data} points: {current_user_points}"

        # Create an inline keyboard with the "Back" and "Close" buttons
        keyboard = [
            [InlineKeyboardButton("Back", callback_data="back"),
             InlineKeyboardButton("Close", callback_data="close")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Edit the original message with the leaderboard and the new inline keyboard
        query.edit_message_text(text=message, parse_mode='Markdown', reply_markup=reply_markup)

    elif data == "back":
        # Call the `leaderboard` function to go back to the previous menu
        leaderboard(update, context)

    elif data == "close":
        # Delete the message
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)


def main() -> None:
    updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs", use_context=True)

    dispatcher = updater.dispatcher

    # Add run_async=True to the MessageHandler
    dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command, count_messages, run_async=True))
    
    dispatcher.add_handler(CallbackQueryHandler(button, pattern='^\w+$', run_async=True))

    dispatcher.add_handler(CommandHandler('leaderboard', leaderboard, run_async=True))
    dispatcher.add_handler(CallbackQueryHandler(leaderboard_callback, pattern='^(group|global|back|close)$', run_async=True))

    updater.start_polling()

if __name__ == '__main__':
    main()
