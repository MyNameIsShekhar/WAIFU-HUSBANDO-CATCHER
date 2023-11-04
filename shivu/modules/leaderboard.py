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


    

async def ctop(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    cursor = group_user_totals_collection.aggregate([
        {"$match": {"group_id": chat_id}},
        {"$project": {"username": 1, "first_name": 1, "character_count": "$count"}},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b>TOP 10 USERS WITH MOST CHARACTERS IN THIS GROUP</b>\n\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username', 'Unknown')
        first_name = escape_markdown(user.get('first_name', 'Unknown'))

        if len(first_name) > 7:
            first_name = first_name[:10] + '...'
        character_count = user['character_count']
        leaderboard_message += f'{i}. <a href="https://t.me/{username}"><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n'
    photo_urls = [
        "https://graph.org/file/38767e79402baa8b04125.jpg",
        "https://graph.org/file/9bbee80d02c720004ab8d.jpg",
        "https://graph.org/file/cd0d8ca9bcfe489a23f82.jpg",
        "https://graph.org//file/e65e9605f3beb5c76026b.jpg",
        "https://graph.org//file/88c0fc2309930c591d98b.jpg"
    ]
    photo_url = random.choice(photo_urls)

    await update.message.reply_photo(photo=photo_url, caption=leaderboard_message, parse_mode='HTML')


async def leaderboard(update: Update, context: CallbackContext) -> None:
    
    cursor = user_collection.aggregate([
        {"$project": {"username": 1, "first_name": 1, "character_count": {"$size": "$characters"}}},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b>TOP 10 USERS WITH MOST CHARACTERS</b>\n\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username', 'Unknown')
        first_name = escape_markdown(user.get('first_name', 'Unknown'))

        if len(first_name) > 7:
            first_name = first_name[:10] + '...'
        character_count = user['character_count']
        leaderboard_message += f'{i}. <a href="https://t.me/{username}"><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n'
    photo_urls = [
        "https://graph.org/file/38767e79402baa8b04125.jpg",
        "https://graph.org/file/9bbee80d02c720004ab8d.jpg",
        "https://graph.org/file/cd0d8ca9bcfe489a23f82.jpg",
        "https://graph.org//file/e65e9605f3beb5c76026b.jpg",
        "https://graph.org//file/88c0fc2309930c591d98b.jpg"
    ]
    photo_url = random.choice(photo_urls)

    await update.message.reply_photo(photo=photo_url, caption=leaderboard_message, parse_mode='HTML')


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


async def stats(update: Update, context: CallbackContext) -> None:
    # Ensure this command is only run by the bot owner for security
    if update.effective_user.id != 6404226395:
        return

    # Get the total unique user ID count
    user_count = await user_collection.count_documents({})

    # Get the total unique group ID count
    group_count = await group_user_totals_collection.distinct('group_id')

    # Send the statistics to the bot owner
    await update.message.reply_text(f'Total Users: {user_count}\nTotal groups: {len(group_count)}')
async def user(update: Update, context: CallbackContext) -> None:
    # Ensure this command is only run by the bot owner for security
    if update.effective_user.id != 6404226395:
        return

    # Check if a user ID was provided
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text('Please provide a user ID.')
        return

    user_id = int(context.args[0])

    # Find the groups the user is in
    cursor = group_user_totals_collection.find({'user_id': user_id})
    groups = await cursor.to_list(length=100)  # Adjust the length as needed

    if not groups:
        await update.message.reply_text('This user is not in any groups.')
        return

    # Construct a message with the group information
    message = f'User {user_id} is in the following groups:\n\n'
    for group in groups:
        group_id = group['group_id']
        group_name = group.get('group_name', 'None')
        username = group.get('username', 'None')
        message += f'Group ID: {group_id}\nGroup Name: {group_name}\nUsername: {username}\n\n'

    await update.message.reply_text(message)

async def leave(update: Update, context: CallbackContext) -> None:
    # Ensure this command is only run by the bot owner for security
    if update.effective_user.id != 6404226395:
        return

    # Check if the bot is in a group chat
    if update.effective_chat.type == 'private':
        await update.message.reply_text(' private chat.')
        return

    # Send a goodbye message
    await update.message.reply_text('I will now leave this group. If you want me back, please DM @oyyshigeoo.')

    # Leave the group
    await context.bot.leave_chat(update.effective_chat.id)


async def snipe(update: Update, context: CallbackContext) -> None:
    # Ensure this command is only run by the bot owner for security
    if update.effective_user.id != 6404226395:
        return

    # Check if a group ID and a message were provided
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text('wroking Shigeoo.')
        return

    group_id = int(context.args[0])
    message_text = ' '.join(context.args[1:])

    # Send the message to the group
    message = await context.bot.send_message(group_id, message_text)

    # Construct the message link if possible
    if message.chat.username and message.chat.type in ['supergroup', 'channel']:
        message_link = f'https://t.me/{message.chat.username}/{message.message_id}'
        await update.message.reply_text(f'Message sent successfully. Message text: "{message_text}". You can view it here.', parse_mode='Markdown')
    else:
        await update.message.reply_text('Error: Message sent successfully, but a message link could not be generated for this chat.')


application.add_handler(CommandHandler('ctop', ctop, block=False))
application.add_handler(CommandHandler('stats', stats, block=False))
application.add_handler(CommandHandler('user', user, block=False))
application.add_handler(CommandHandler('leave', leave, block=False))
application.add_handler(CommandHandler('snipe', snipe, block=False))


application.add_handler(CommandHandler('top', leaderboard, block=False))
application.add_handler(CommandHandler('broadcast', broadcast))

