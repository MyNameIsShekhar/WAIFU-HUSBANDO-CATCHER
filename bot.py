from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from pymongo import MongoClient
from PIL import Image, ImageDraw, ImageFont
import random
import io
import time
import requests 
from io import BytesIO

from wordlist import word_list

client = MongoClient("mongodb+srv://shuyaaaaa12:NvpoBuRp7MVPcAYA@cluster0.q2yycqx.mongodb.net/")
db = client['telegram_bot']
users = db['bhaii']  # Each document in this collection will now have a 'coins' field that is a dictionary mapping group_id to coins
groups = db['sahabb']
# Each document in this collection will now have a 'words' field that is a list of words that have been sent in the group
# Current word to guess and message count




current_word = None
message_count = 0
word_guessed = False
word_time = None



# Define image URL lists





# Define fonts list


def generate_image(word: str) -> io.BytesIO:
    fonts = ['assets/adrip1.ttf',]  # List of fonts
    images = ['assets/392eb296b941c76ebd423bc383b0e970.jpg',]  # List of images

    font_path = random.choice(fonts)  # Randomly choose a font
    image_path = random.choice(images)  # Randomly choose an image

    img = Image.open(image_path)  # Load background image
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 50)  # Load font
    text_color = (255, 255, 255)  # White color
    text_size = d.textsize(word, font)
    text_xy = ((img.width - text_size[0]) / 2, (img.height - text_size[1]) / 2)  # Center the text
    d.text(text_xy, word, fill=text_color, font=font)
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='JPEG')
    byte_arr.seek(0)
    return byte_arr

def handle_message(update: Update, context: CallbackContext) -> None:
    global current_word, message_count, word_guessed, word_time
    message_count += 1
    if message_count >= 10:
        message_count = 0
        group_id = update.effective_chat.id
        group_data = groups.find_one({"group_id": group_id})
        if group_data is None:
            groups.insert_one({"group_id": group_id, "words": []})
            available_words = word_list.copy()
        else:
            available_words = list(set(word_list) - set(group_data['words']))
            if not available_words:  # If all words have been used in this group, reset the list of used words
                groups.update_one({"group_id": group_id}, {"$set": {"words": []}})
                available_words = word_list.copy()
        current_word = random.choice(available_words)
        groups.update_one({"group_id": group_id}, {"$push": {"words": current_word}})
        img_stream = generate_image(current_word)
        
        # Create an inline keyboard button for updates
        keyboard = [[InlineKeyboardButton("Updates", url='https://t.me/nezukoupdate')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send the image with the inline keyboard button and a caption
        context.bot.send_photo(chat_id=update.effective_chat.id,
                               photo=img_stream,
                               caption=f"𝙉𝙚𝙬 𝙒𝙤𝙧𝙙 𝘼𝙥𝙥𝙚𝙖𝙧𝙚𝙙.. 𝙒𝙧𝙞𝙩𝙚 𝙁𝙖𝙨𝙩 𝙖𝙣𝙙 𝙂𝙚𝙩 𝘾𝙤𝙞𝙣𝙨𝙨𝙨..!!!",
                               reply_markup=reply_markup)
        
        word_guessed = False
        word_time = time.time()  # Start the timer

    elif not word_guessed and update.message.text.lower() == current_word.lower():
        elapsed_time = time.time() - word_time
        user_id = update.message.from_user.id
        first_name = update.message.from_user.first_name
        username = update.message.from_user.username 
        group_id = update.effective_chat.id
        user_data = users.find_one({"user_id": user_id})
        if user_data is None:
            users.insert_one({"user_id": user_id,
                              "first_name": first_name,
                              "username": username,
                              "coins": {str(group_id): 5},
                              "global_coins": 5})
            coins = 5
            global_coins = 5

        else:
            coins = user_data['coins'].get(str(group_id), 0) + 5
            global_coins = user_data.get('global_coins', 0) + 5
            users.update_one({"user_id": user_id},
                             {"$set": {f"coins.{group_id}": coins,
                                       "first_name": first_name,
                                       "username": username,
                                       "global_coins": global_coins}})
        
        minutes, seconds = divmod(elapsed_time, 60)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Correct [{first_name}](https://t.me/{username})! You now have {coins} coins in this group. You guessed the word in {int(minutes)}m {int(seconds)}s.",
                                 disable_web_page_preview=True,
                                 parse_mode='Markdown',)
        word_guessed = True


def leaderboard(update: Update, context: CallbackContext) -> None:
    group_id = update.effective_chat.id
    leaderboard_data = users.find().sort(f"coins.{group_id}", -1).limit(10)
    leaderboard_text = "*Group Leaderboard*\n\n"
    for i, data in enumerate(leaderboard_data):
        first_name= data.get('first_name', 'Unknown')
        username= data.get('username', 'nezukoolmao')
        coins = data['coins'].get(str(group_id), 0)
        leaderboard_text += f"{i+1}. {first_name}- {coins}\n"
    keyboard = [[InlineKeyboardButton("Global", callback_data='leaderboard_global')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text=leaderboard_text, reply_markup=reply_markup, disable_web_page_preview=True, parse_mode='Markdown')

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'global':
        leaderboard_data = users.find().sort("global_coins", -1).limit(10)
        leaderboard_text = "*Global Leaderboard*\n\n"
        
        for i, data in enumerate(leaderboard_data):
            first_name = data.get('first_name', 'Unknown')
            username = data.get('username','nezukoolmao')
            coins = data.get('global_coins', 0)
            
            leaderboard_text += f"{i+1}. [{first_name}](https://t.me/{username})- {coins}\n"
        
        keyboard = [[InlineKeyboardButton("Group", callback_data='group')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(text=leaderboard_text, reply_markup=reply_markup,disable_web_page_preview=True, parse_mode='Markdown',)

    elif query.data == 'group':
        group_id = update.effective_chat.id
        leaderboard_data = users.find().sort(f"coins.{group_id}", -1).limit(10)
        
        leaderboard_text = "*Group Leaderboard*\n\n"
        
        for i, data in enumerate(leaderboard_data):
            first_name= data.get('first_name', 'Unknown')
            username= data.get('username', 'nezukoolmao')
            coins = data['coins'].get(str(group_id), 0)
            
            leaderboard_text += f"{i+1}. [{first_name}](https://t.me/{username}) - {coins}\n"
        
        keyboard = [[InlineKeyboardButton("Global", callback_data='global')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(text=leaderboard_text, reply_markup=reply_markup,parse_mode='Markdown',disable_web_page_preview=True)



def help_command(update, context):
    update.message.reply_text('Here are the commands you can use:\n'
                              '/start - Start the bot\n'
                              '/help - Show this help message\n'
                              '/leaderboard - see Top Coin Holders'
                             )

def main() -> None:
    updater = Updater(token='6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs')

    dispatcher = updater.dispatcher

    
    
    message_handler = MessageHandler(Filters.text & ~Filters.command, handle_message)
    dispatcher.add_handler(message_handler)

    
    
    dispatcher.add_handler(CommandHandler('help', help_command))
  
    # Add these handlers to your dispatcher
    dispatcher.add_handler(CommandHandler('leaderboard', leaderboard))
    dispatcher.add_handler(CallbackQueryHandler(button))
    
    

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
