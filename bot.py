from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from pymongo import MongoClient
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

# Connect to MongoDB
client = MongoClient("mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority")
db = client["telegrambbot"]
questions_db = db["questions"]

# Load questions from MongoDB
questions = list(questions_db.find({}))

users_attempted = {}

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not questions:
        # Load questions from MongoDB
        questions.extend(list(questions_db.find({})))
    question = questions.pop(0)
    keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in question['options']]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_photo(chat_id=user.id, photo=question['image'], caption=question['caption'], reply_markup=reply_markup)
    
    # Reset the attempts for all users
    users_attempted.clear()

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    if user_id in users_attempted:
        query.answer("You've already tried.")
    else:
        users_attempted[user_id] = True
        if query.data == questions[0]['answer']:
            # Add 5 coins to the user's account
            users.update_one({"_id": user_id}, {"$inc": {"group_coins": 5, "global_coins": 5}}, upsert=True)
            query.edit_message_text(f"Congratulations {query.from_user.first_name}! You've earned 5 coins.")
        else:
            query.answer("Your answer is wrong.")

def add(update: Update, context: CallbackContext) -> None:
    # This function will be called when the /add command is issued.
    # It expects the question data to be sent as a single message in the following format:
    # /add <image_url>;<caption>;<option1>;<option2>;<option3>;<option4>;<answer>
    data = update.message.text.split(' ', 1)
    if len(data) != 2 or len(data[1].split(';')) != 7:
        update.message.reply_text("Invalid format. Please use: /add <image_url>;<caption>;<option1>;<option2>;<option3>;<option4>;<answer>")
        return

    data = data[1].split(';')
    question = {
        "image": data[0],
        "caption": data[1],
        "options": data[2:6],
        "answer": data[6]
    }
    
    try:
        questions_db.insert_one(question)
        update.message.reply_text(f"Question added successfully by {update.message.from_user.first_name}.")
    except Exception as e:
        logger.error(e)
        update.message.reply_text("Failed to add question.")

def main() -> None:
    updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs", use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
