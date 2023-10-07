from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# Define your images, options, and correct answers here
quiz = [
    {
        "image_url": "https://graph.org/file/cb384e79bc3ff2a36e1fa.jpg",
        "options": ["Salad", "Beef Steak", "Hamburger"],
        "answer": "Hamburger"
    },
    {
        "image_url": "https://graph.org/file/60dcb0e5dc76ad24d52b8.jpg",
        "options": ["Pizza", "Pasta", "Lasagna"],
        "answer": "Pizza"
    },
    # Add more images and options here
]


def start(update: Update, context: CallbackContext) -> None:
    for i, q in enumerate(quiz):
        question = f"What is this food? (Question {i+1})"
        keyboard = [[InlineKeyboardButton(o, callback_data=f"{i}:{o}")] for o in q["options"]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=q["image_url"], caption=question, reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    i, answer = query.data.split(":")
    if answer == quiz[int(i)]["answer"]:
        query.edit_message_text(text=f"Correct! You've earned a coin.")
    else:
        query.edit_message_text(text=f"Sorry, that's not correct.")

def main() -> None:
    updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
