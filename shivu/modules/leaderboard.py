from itertools import groupby
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
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
import json

import re

def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)




collection = db['anime_characters_lol']
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totalsssssss']

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import random


    img_url_list = [
        "https://graph.org/file/38767e79402baa8b04125.jpg",
        "https://graph.org/file/9bbee80d02c720004ab8d.jpg",
        "https://graph.org/file/cd0d8ca9bcfe489a23f82.jpg",
        "https://graph.org//file/e65e9605f3beb5c76026b.jpg",
        "https://graph.org//file/88c0fc2309930c591d98b.jpg"
    ]

async def group_leaderboard(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    # Get the top 10 users in the group
    top_users = group_user_totals_collection.find(
        {'group_id': chat_id},
        sort=[('count', -1)],
        limit=10
    )

    # Prepare the leaderboard text
    leaderboard_text = 'Group Leaderboard 🏆\n\n'
    for i, user in enumerate(top_users, start=1):
        user_info = await user_collection.find_one({'id': user['user_id']})
        username = user_info.get('username', 'Unknown User')
        count = user['count']
        leaderboard_text += f'{i}. {username}: {count} guesses\n'

    # Get a random image URL from your list
    image_url = random.choice(image_url_list)

    # Send the image with the leaderboard as caption
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=image_url,
        caption=leaderboard_text
    )

async def leaderboard(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton('My Rank', callback_data='leaderboard_myrank')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    cursor = user_collection.aggregate([
        {"$project": {"username": 1, "first_name": 1, "character_count": {"$size": "$characters"}}},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "***TOP 10 USERS WITH MOST CHARACTERS***\n\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username', 'Unknown')
        first_name = escape_markdown(user.get('first_name', 'Unknown'))

        if len(first_name) > 7:
            first_name = first_name[:10] + '...'
        character_count = user['character_count']
        leaderboard_message += f'{i}. {first_name}- {character_count} characters\n'

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

    user = await user_collection.find_one({'id': query.from_user.id})
    
    if user is None:
        await query.answer('You are not in this rank.', show_alert=True)
        return

    user_character_count = len(user['characters'])

    cursor = user_collection.aggregate([
        {"$project": {"character_count": {"$size": "$characters"}}},
        {"$sort": {"character_count": -1}}
    ])
    sorted_counts = [doc['character_count'] for doc in await cursor.to_list(length=100)]

    user_rank = sorted_counts.index(user_character_count) + 1

    await query.answer(f'Your rank is {user_rank}.', show_alert=True)


async def broadcast(update: Update, context: CallbackContext) -> None:
    
    if str(update.effective_user.id) == '6404226395':
        
        if update.message.reply_to_message is None:
            await update.message.reply_text('Please reply to a message to broadcast.')
            return

        
        all_users = await user_collection.find({}).to_list(length=None)
        all_groups = await group_user_totals_collection.find({}).to_list(length=None)
        
        unique_user_ids = set(user['id'] for user in all_users)
        unique_group_ids = set(group['group_id'] for group in all_groups)

        total_sent = 0
        total_failed = 0

        
        for user_id in unique_user_ids:
            try:
                await context.bot.forward_message(chat_id=user_id, from_chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
                total_sent += 1
            except Exception:
                total_failed += 1

        
        for group_id in unique_group_ids:
            try:
                await context.bot.forward_message(chat_id=group_id, from_chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
                total_sent += 1
            except Exception:
                total_failed += 1

        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Broadcast report:\n\nTotal messages sent successfully: {total_sent}\nTotal messages failed to send: {total_failed}'
        )
    else:
        await update.message.reply_text('Only Shigeo Can use')


import json
import os

async def user(update: Update, context: CallbackContext) -> None:
    
    if str(update.effective_user.id) == '6404226395':
        
        all_users = await user_collection.find({}).to_list(length=None)
        
        
        users = Element('users')
        for user in all_users:
            user_element = SubElement(users, 'user')
            for key, value in user.items():
                SubElement(user_element, key).text = str(value)
        output = parseString(tostring(users)).toprettyxml(indent="  ")
        
        
        with open('users.xml', 'w') as f:
            f.write(output)
                
        
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open('users.xml', 'rb'))
        
        
        os.remove('users.xml')
    else:
        await update.message.reply_text('You are not authorized to use this command.')

async def group(update: Update, context: CallbackContext) -> None:
    
    if str(update.effective_user.id) == '6404226395':
        
        all_groups = await group_user_totals_collection.find({}).to_list(length=None)
        

        groups = Element('groups')
        for group in all_groups:
            group_element = SubElement(groups, 'group')
            for key, value in group.items():
                SubElement(group_element, key).text = str(value)
        output = parseString(tostring(groups)).toprettyxml(indent="  ")
        
        
        with open('groups.xml', 'w') as f:
            f.write(output)
        
        
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open('groups.xml', 'rb'))
        
        
        os.remove('groups.xml')
    else:
        await update.message.reply_text('You are not authorized to use this command.')


application.add_handler(CommandHandler('grouptop', group_leaderboard, block=False))
application.add_handler(CommandHandler('globaltop', leaderboard, block=False))
application.add_handler(CallbackQueryHandler(leaderboard_button, pattern='^leaderboard_',block=False))
application.add_handler(CommandHandler('broadcast', broadcast))
application.add_handler(CommandHandler('users', user))
application.add_handler(CommandHandler('groups', group))

