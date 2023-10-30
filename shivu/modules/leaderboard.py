from itertools import groupby
from telegram import InputMediaPhoto
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent, InputMediaPhoto
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from telegram import Update
from motor.motor_asyncio import AsyncIOMotorClient 
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters, Application
from telegram.ext import InlineQueryHandler,CallbackQueryHandler, ChosenInlineResultHandler
from pymongo import MongoClient, ReturnDocument
import urllib.request
from shivu import application 
from shivu import db
import random

collection = db['anime_characters_lol']
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totalssssss']

async def leaderboard(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton('My Rank', callback_data='leaderboard_myrank')],
        [InlineKeyboardButton('Group Leaderboard', callback_data='group_leaderboard')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    cursor = user_collection.find().sort('total_count', -1).limit(10)
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "***TOP 10 MOST GUESSED USERS***\n\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username', 'Unknown')
        first_name = user.get('first_name', 'Unknown')
        if len(first_name) > 7:
            first_name = first_name[:10] + '...'
        count = user['total_count']
        leaderboard_message += f'{i}. {first_name}- {count}\n'

    photo_urls = [
        "https://graph.org/file/38767e79402baa8b04125.jpg",
        "https://graph.org/file/9bbee80d02c720004ab8d.jpg",
        "https://graph.org/file/cd0d8ca9bcfe489a23f82.jpg",
        "https://graph.org//file/e65e9605f3beb5c76026b.jpg",
        "https://graph.org//file/88c0fc2309930c591d98b.jpg"
    ]
    photo_url = random.choice(photo_urls)

    await update.message.reply_photo(photo=photo_url, caption=leaderboard_message, reply_markup=reply_markup, parse_mode='Markdown')

async def leaderboard_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    if data == 'leaderboard_myrank':
        user_total = await user_collection.find_one({'id': query.from_user.id})
    
        if user_total is None:
            await query.answer('You are not in this rank.', show_alert=True)
            return

        user_total_count = user_total['total_count']

        cursor = user_collection.find({}, {'total_count': 1, '_id': 0})
        sorted_counts = sorted(await cursor.to_list(length=100), key=lambda x: x['total_count'], reverse=True)

        user_rank = sorted_counts.index({'total_count': user_total_count}) + 1

        await query.answer(f'Your rank is {user_rank}.', show_alert=True)
        
    elif data == 'group_leaderboard':
        keyboard = [
            [InlineKeyboardButton('My Rank', callback_data='group_leaderboard_myrank')],
            [InlineKeyboardButton('Global Leaderboard', callback_data='global_leaderboard')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        cursor = group_user_totals_collection.find({'group_id': query.message.chat.id}).sort('total_count', -1).limit(10)
        leaderboard_data = await cursor.to_list(length=10)

        leaderboard_message = "***TOP 10 MOST GUESSED USERS IN THIS GROUP***\n\n"

        for i, user in enumerate(leaderboard_data, start=1):
            username = user.get('username', 'Unknown')
            first_name = user.get('first_name', 'Unknown')
            if len(first_name) > 7:
                first_name = first_name[:10] + '...'
            count = user['total_count']
            leaderboard_message += f'{i}. {first_name}- {count}\n'

        await query.edit_message_caption(caption=leaderboard_message, reply_markup=reply_markup, parse_mode='Markdown')
      
application.add_handler(CommandHandler('leaderboard', leaderboard, block=False))
application.add_handler(CallbackQueryHandler(leaderboard_button, pattern='^leaderboard_', block=False))
application.add_handler(CallbackQueryHandler(leaderboard_button, pattern='^group_leaderboard$', block=False))

