from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pymongo import MongoClient
import random

# Connect to MongoDB
client = MongoClient('your_mongodb_connection_string')
db = client['telegram_bot']
collection = db['images']

def upload(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message.photo:
        file = context.bot.getFile(update.message.reply_to_message.photo[-1].file_id)
        image_name = ' '.join(context.args)
        image_id = file.file_id
        collection.insert_one({'_id': image_id, 'name': image_name})
        update.message.reply_text('Upload done')
    else:
        update.message.reply_text('Something wrong')

def guess(update: Update, context: CallbackContext) -> None:
    image_name = ' '.join(context.args)
    image = collection.find_one({'name': image_name})
    if image:
        # Add coins to the user's account
        update.message.reply_text('Correct guess! You get coins.')
    else:
        update.message.reply_text('Incorrect guess.')

def handle_messages(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type == 'group':
        if 'counter' not in context.chat_data:
            context.chat_data['counter'] = 0
        context.chat_data['counter'] += 1
        if context.chat_data['counter'] % 10 == 0:
            images = list(collection.find())
            if images:
                selected_image = random.choice(images)
                context.bot.send_photo(chat_id=update.message.chat_id, photo=selected_image['_id'])

def main() -> None:
    updater = Updater(token='6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs')

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('upload', upload))
    dispatcher.add_handler(CommandHandler('guess', guess))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_messages))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
