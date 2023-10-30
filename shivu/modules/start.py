import csv
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from motor.motor_asyncio import AsyncIOMotorClient
from telegram.ext import MessageHandler, filters

from telegram.ext import CommandHandler
from shivu import application 
import random

caption = """
        🌟 𝗚𝗲𝘁 𝗿𝗲𝗮𝗱𝘆 𝗳𝗼𝗿 𝘀𝗼𝗺𝗲 𝗴𝗮𝗺𝗶𝗻𝗴 𝗳𝘂𝗻! [🎮] 𝗧𝗮𝗽 𝗼𝗻 𝗵𝗲𝗹𝗽 𝗮𝗻𝘆𝘁𝗶𝗺𝗲 𝗶𝗳 𝘆𝗼𝘂 𝗻𝗲𝗲𝗱 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝗰𝗲 𝗼𝗿 𝘀𝘁𝗮𝗿𝘁 𝘁𝗼 𝗯𝗲𝗴𝗶𝗻 𝘆𝗼𝘂𝗿 𝗳𝗶𝗿𝘀𝘁 𝗮𝗱𝘃𝗲𝗻𝘁𝘂𝗿𝗲
        """

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
    ***Help Section :***
    
/guess: ***To Guess character (only works in group)***
/fav: ***Add Your fav***
/give: ***Give any Character from Your Collection to another user.. (only works in groups)***
/collection: ***to see Your Collection***
/grouptop: ***See Top Group users in group (only Works in Groups)***
/globaltop: ***To See Top Global Users***
/changetime: ***Change Character appear time (only works in Groups)***
   """
        keyboard = [[InlineKeyboardButton("Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':
        caption = """
        🌟 𝗚𝗲𝘁 𝗿𝗲𝗮𝗱𝘆 𝗳𝗼𝗿 𝘀𝗼𝗺𝗲 𝗴𝗮𝗺𝗶𝗻𝗴 𝗳𝘂𝗻! [🎮] 𝗧𝗮𝗽 𝗼𝗻 𝗵𝗲𝗹𝗽 𝗮𝗻𝘆𝘁𝗶𝗺𝗲 𝗶𝗳 𝘆𝗼𝘂 𝗻𝗲𝗲𝗱 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝗰𝗲 𝗼𝗿 𝘀𝘁𝗮𝗿𝘁 𝘁𝗼 𝗯𝗲𝗴𝗶𝗻 𝘆𝗼𝘂𝗿 𝗳𝗶𝗿𝘀𝘁 𝗮𝗱𝘃𝗲𝗻𝘁𝘂𝗿𝗲
        """
        keyboard = [
            [InlineKeyboardButton("Help", callback_data='help')],
            [InlineKeyboardButton("Support", url=f'https://t.me/collect_em_all')],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=caption, reply_markup=reply_markup)


sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651','5813403535', '6393627898', '5952787198', '6614280216','6248411931','5216262234','1608353423']

async def stats(update: Update, context: CallbackContext) -> None:
    # Check if the command is issued by the owner
    if str(update.effective_user.id) == '6404226395':
        # Get all users from the collection
        all_users = await user_collection.find({}).to_list(length=None)
        
        # Create a set to store unique user ids
        unique_user_ids = set()
        
        for user in all_users:
            unique_user_ids.add(user['id'])
        
        # Send the count of unique users
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Total users: {len(unique_user_ids)}'
        )
    else:
        await update.message.reply_text('Lol')

async def explore(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    if user_id not in sudo_users:
        return

    # Fetch all users data
    cursor = collection.find({})
    users_data = await cursor.to_list(length=100)

    # Prepare data for CSV
    fieldnames = ['_id', 'username', 'first_name']
    rows = [{fieldname: user_data.get(fieldname, '') for fieldname in fieldnames} for user_data in users_data]

    # Write data to CSV file
    filename = 'users_data.csv'
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Send the CSV file
    with open(filename, 'rb') as csvfile:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=csvfile)

    # Delete the CSV file
    os.remove(filename)

# Add handlers to the application

application.add_handler(CommandHandler('stats', stats))

# Add explore handler to the application
explore_handler = CommandHandler('explore', explore)
application.add_handler(explore_handler)


application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$'))

start_handler = CommandHandler('start', start)
application.add_handler(start_handler)
