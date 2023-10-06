from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import random

# Replace 'TOKEN' with your Bot's API token.
updater = Updater(token='6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs', use_context=True)

# This is your list of quiz questions, answers and images.
 
quiz_list = [
    {"question": "Question 1", "options": ["Option 1", "Option 2", "Option 3"], "answer": 0, "image": "https://graph.org/file/bce79a4a7b2e5e73dc37a.jpg"},
    {"question": "Question 2", "options": ["Option 1", "Option 2", "Option 3"], "answer": 1, "image": "https://graph.org/file/314324a8e1831137c8f94.jpg"},
    # Add more questions here.
]

# This will store the coins for each user.
user_data = {}

def start(update: Update, context: CallbackContext) -> None:
    quiz = random.choice(quiz_list)
    context.chat_data['quiz'] = quiz

    keyboard = [[InlineKeyboardButton(option, callback_data=str(i))] for i, option in enumerate(quiz["options"])]

    context.bot.send_photo(chat_id=update.effective_chat.id, photo=quiz["image"])
    context.bot.send_message(chat_id=update.effective_chat.id, text=quiz["question"], reply_markup=InlineKeyboardMarkup(keyboard))

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if int(query.data) == context.chat_data['quiz']["answer"]:
        user_id = update.effective_user.id
        if user_id not in user_data:
            user_data[user_id] = 0
        user_data[user_id] += 1
        query.edit_message_text(text=f"Correct! You now have {user_data[user_id]} coins.")
    else:
        query.edit_message_text(text="Sorry, that's incorrect.")

def main() -> None:
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
