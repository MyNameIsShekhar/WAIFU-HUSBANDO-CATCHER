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



photo_url_list = ["https://graph.org/file/38767e79402baa8b04125.jpg", 'https://telegra.ph/file/c940700435ff6d27bf49d.jpg']
caption = f"""
        ***Hey there! {update.effective_user.first_name} 🌻***
        
        
i Am Collect 'Em All Bot.. Add Me in You're Group And I will send Random Characters in group after every 100 messages and who guessed that character's name Correct.. I will add That Character in That user's Collection.. Tap on help Button To See All Commands
        """
keyboard = [
            [InlineKeyboardButton("Add Me", url=f'http://t.me/Collect_emAll_Bot?startgroup=new')],
        
            [InlineKeyboardButton("Help", callback_data='help'),
             InlineKeyboardButton("Support", url=f'https://t.me/collect_em_all')],
            [InlineKeyboardButton("Updates", url=f'https://t.me/CollectEmAllUpdates')],
           
    ]

async def start(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.type != "private":
        return

    
    
    photo_url = random.choice(photo_url_list)
    
    
    
    reply_markupp = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """
    ***Help Section :***
    
/guess: To Guess character (only works in group)
/fav: Add Your fav
/give: Give any Character from Your Collection to another user.. (only works in groups)
/collection: to see Your Collection
/grouptop: See Top Group users in group (only Works in Groups)
/globaltop: To See Top Global Users***
/changetime: Change Character appear time (only works in Groups)
   """
        help_keyboard = [[InlineKeyboardButton("Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)
        
        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':

        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=caption, reply_markup=reply_markup, parse_mode='markdown')



application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$'))

start_handler = CommandHandler('start', start)
application.add_handler(start_handler)
