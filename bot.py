from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import schedule
import time

class ImageBot:
    def __init__(self):
        self.updater = Updater(token='6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs', use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.images = [('https://graph.org/file/bce79a4a7b2e5e73dc37a.jpg', 'Naruto Uzumaki'), ('https://graph.org/file/314324a8e1831137c8f94.jpg', 'Hinata')]  # Add your image URLs here
        self.current_image = None

    def start(self, update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    def send_image(self):
    if self.images:  # Check if there are any images left
        self.current_image = self.images.pop(0)  # Get the next image from the list
        self.updater.bot.send_photo(chat_id=chat_id, photo=self.current_image[0])

    def run(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        schedule.every(1).minutes.do(self.send_image)

        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    bot = ImageBot()
    bot.run()
