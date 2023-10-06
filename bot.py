from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

class ImageBot:
    def __init__(self):
        self.updater = Updater(token='6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs', use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.message_count = 0
        self.images = ('https://graph.org/file/bce79a4a7b2e5e73dc37a.jpg', 'Naruto Uzumaki'), ('https://graph.org/file/314324a8e1831137c8f94.jpg', 'Hinata')]  # Add your image URLs here
        self.current_image = None

    def start(self, update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    def count_messages(self, update: Update, context: CallbackContext):
        self.message_count += 1
        if self.message_count >= 10:
            self.message_count = 0
            self.current_image = self.images.pop(0)  # Get the next image from the list
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=self.current_image[0])

    def guess(self, update: Update, context: CallbackContext):
        if ' '.join(context.args) == self.current_image[1]:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Correct! You get 5 coins.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, that's not correct.")

    def run(self):
        start_handler = CommandHandler('start', self.start)
        message_handler = MessageHandler(Filters.text & (~Filters.command), self.count_messages)
        guess_handler = CommandHandler('guess', self.guess)

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(message_handler)
        self.dispatcher.add_handler(guess_handler)

        self.updater.start_polling()

if __name__ == '__main__':
    bot = ImageBot()
    bot.run()
