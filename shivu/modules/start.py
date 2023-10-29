from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from motor.motor_asyncio import AsyncIOMotorClient
from telegram.ext import CommandHandler
from shivu import application 
import random


client = AsyncIOMotorClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
db = client['your_database_name']  # replace with your database name
collection = db['your_collection_name']  # replace with your collection name

photo_url_list = ["https://graph.org/file/38767e79402baa8b04125.jpg"]  # replace with your list of photo URLs

async def start(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.type != "private":
        return

    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await collection.find_one({'_id': user_id})

    if not user_data:
        user_data = {
            '_id': user_id,
            'first_name': first_name,
        }
        if username:
            user_data['username'] = username
        await collection.insert_one(user_data)

    
    photo_url = random.choice(photo_url_list)
    
    caption = """
        Hey.. Tap On help To See All my Commands
        """
    keyboard = [
        [InlineKeyboardButton("Help", callback_data='help')],
        [InlineKeyboardButton("Support", url=f'https://t.me/collect_em_all')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup)


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
   await query.answer()

    if query.data == 'help':
        help_text = """
        Help Section : 
      
        /guess: To Guess character (only works in group)
        /fav: Add Your fav
        /give: Give any Character from Your Collection to another user.. (only works in groups)
        /collection: to see Your Collection 
        /grouptop: See Top Group users in group (only Works in Groups)
        /globaltop: To See Top Global Users
        /changetime: Change Character appear time (only works in Groups)
        
        """
        await query.message.edit_photo(help_text)


button_handler = CallbackQueryHandler(button)
application.add_handler(button_handler)


start_handler = CommandHandler('start', start)
application.add_handler(start_handler)
