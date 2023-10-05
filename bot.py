from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from pymongo import MongoClient
import requests
import os

# Initialize MongoDB client
client = MongoClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')
db = client['mydatabase']
collection = db['mycollection']

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Send me a photo with /upload [image name]')

def upload(update: Update, context: CallbackContext) -> None:
    # Check if photo is included in the message
    if update.message.photo:
        # Get file_id of the photo
        file_id = update.message.photo[-1].file_id

        # Get image name from the command
        image_name = ' '.join(context.args)

        # Get the photo file
        photo_file = context.bot.get_file(file_id)

        # Download the photo to local directory
        photo_file.download(image_name)

        # Save the photo in MongoDB
        with open(image_name, "rb") as f:
            binary_data = f.read()

        # Insert into MongoDB (you might want to use GridFS if the file is large)
        collection.insert_one({"image_name": image_name, "image_data": binary_data})

        # Delete the local file as it's already saved in MongoDB
        os.remove(image_name)

        update.message.reply_text('Upload done')
    else:
        update.message.reply_text('Please reply a photo with /upload [image name]')

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("upload", upload))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
