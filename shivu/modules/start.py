import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram.ext import MessageHandler, filters
from telegram.ext import CommandHandler
from shivu import application 
from shivu import db, photo_urls, GROUP_ID
import random
collection = db['total_pm_usersss']


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:
        
        await collection.insert_one({"_id": user_id, "first_name": first_name, "username": username})
        
        await context.bot.send_message(chat_id=GROUP_ID, text=f"<a href='tg://user?id={user_id}'>{first_name}</a>", parse_mode='HTML')
    else:
        
        if user_data['first_name'] != first_name or user_data['username'] != username:
            
            await collection.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username}})

    

    if update.effective_chat.type== "private":
        
        
        caption = f"""
        ***Hey there! {update.effective_user.first_name} 🌻***
              
***i Am Collect 'Em All Bot.. Add Me in You're Group And I will send Random Characters in group after every 100 messages and who guessed that character's name Correct.. I will add That Character in That user's Collection.. Tap on help Button To See All Commands***
               """
        keyboard = [
            [InlineKeyboardButton("Add Me", url=f'http://t.me/Collect_emAll_Bot?startgroup=new')],
            [InlineKeyboardButton("Help", callback_data='help'),
             InlineKeyboardButton("Support", url=f'https://t.me/collect_em_all')],
            [InlineKeyboardButton("Updates", url=f'https://t.me/CollectEmAllUpdates')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        photo_url = random.choice(photo_urls)

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

    else:
        photo_url = random.choice(photo_urls)
        keyboard = [
            
            [InlineKeyboardButton("Help", callback_data='help'),
             InlineKeyboardButton("Support", url=f'https://t.me/collect_em_all')],
            
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption="I am alive",reply_markup=reply_markup )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """
    ***Help Section :***
    
***/guess: To Guess character (only works in group)***
***/fav: Add Your fav***
***/trade : To trade Characters***
***/gift: Give any Character from Your Collection to another user.. (only works in groups)***
***/collection: To see Your Collection***
***/topgroups : See Top Groups.. Ppl Guesses Most in that Groups***
***/top: Too See Top Users***
***/ctop : Your ChatTop***
***/changetime: Change Character appear time (only works in Groups)***
   """
        help_keyboard = [[InlineKeyboardButton("Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)
        
        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':

        caption = f"""
        ***Hey there! {update.effective_user.first_name}*** 🌻
        
***i Am Collect 'Em All Bot.. Add Me in You're Group And I will send Random Characters in group after every 100 messages and who guessed that character's name Correct.. I will add That Character in That user's Collection.. Tap on help Button To See All Commands***
        """
        keyboard = [
            [InlineKeyboardButton("Add Me", url=f'http://t.me/Collect_emAll_Bot?startgroup=new')],
            [InlineKeyboardButton("Help", callback_data='help'),
             InlineKeyboardButton("Support", url=f'https://t.me/collect_em_all')],
            [InlineKeyboardButton("Updates", url=f'https://t.me/CollectEmAllUpdates')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$'))
start_handler = CommandHandler('start', start)
application.add_handler(start_handler)
