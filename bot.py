from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import random


# This is your list of quiz questions, answers and images.
 

# List of questions. Each question is a dictionary with 'image', 'options' and 'answer'
questions = [
    {'image': 'https://graph.org/file/314324a8e1831137c8f94.jpg', 'options': ['Naruto', 'Sasuke', 'Sakura', 'Orochimaru'], 'answer': 'Naruto'},
    # Add more questions here
]

def start(update: Update, context: CallbackContext) -> None:
    # Select a random question
    question = random.choice(questions)
    context.chat_data['answer'] = question['answer']

    keyboard = [[InlineKeyboardButton(opt, callback_data=opt) for opt in question['options']]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the image with the options
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=question['image'], caption="Guess the image name", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered
    query.answer()

    if query.data == context.chat_data['answer']:
        query.edit_message_text(text="Correct answer! You get coins!")
    else:
        query.edit_message_text(text="That's wrong!")

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs", use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
