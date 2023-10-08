from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from pymongo import MongoClient
from PIL import Image, ImageDraw, ImageFont

import random
# Connect to your MongoDB
client = MongoClient('mongodb+srv://shuyaaaaa12:NvpoBuRp7MVPcAYA@cluster0.q2yycqx.mongodb.net/')
db = client['telegram_bot']
users = db['users']

TOKEN = '6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs'
FONT_PATH ='assets/adrip1.ttf'  # Update this to the path of your font file

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    context.user_data['coins'] = 0

    # Store user data in MongoDB
    users.insert_one({'user_id': user.id, 'coins': 0})

    update.message.reply_text(f'Hello {user.first_name}! Let\'s start learning Japanese.')

def send_word(update: Update, context: CallbackContext) -> None:
    words = [
        {"japanese": "konnichiwa", "english": "Hello", "options": ["Goodbye", "Thank you", "Yes", "No"]},
        {"japanese": "arigatou", "english": "Thank you", "options": ["Hello", "Goodbye", "Yes", "No"]},
    ]

    # Select a random word
    word = random.choice(words)
    context.user_data['current_word'] = word
    context.user_data['tried'] = False

    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in word['options']]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Draw text on image
    image_path = 'assets/392eb296b941c76ebd423bc383b0e970.jpg'  # Update this to the path of your image file
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, size=45)
    draw.text((100, 100), word["japanese"], fill='rgb(0, 0, 0)', font=font)

    # Save the image and send it
    image.save('output.jpg')
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('output.jpg', 'rb'), caption="Tap On correct English Meaning Word and get coins", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    selected_option = query.data
    current_word = context.user_data.get('current_word', {})

    if selected_option == current_word.get('english'):
        # Increase coins and update in MongoDB
        context.user_data['coins'] += 5
        users.update_one({'user_id': query.from_user.id}, {'$inc': {'coins': 5}})

        query.delete_message()
        context.bot.send_message(chat_id=query.message.chat_id, text=f"Correct! @{query.from_user.username} now has {context.user_data['coins']} coins.")
        send_word(update, context)
    else:
        if not context.user_data.get('tried', False):
            query.answer(show_alert=True)
            query.edit_message_text(text="You're wrong. Try again.")
            context.user_data['tried'] = True
        else:
            query.answer(show_alert=True)
            query.edit_message_text(text="You've already tried. Wait for the next word.")

def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("send_word",send_word))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
