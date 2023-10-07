# Simple Rps Bot by @SleepyShuyaa


import random
from operator import itemgetter
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from datetime import datetime, timedelta
from Zenistuu- import shuyaa

# Initialize the MongoDB client
mongo_client = MongoClient("YOUR MongoDB URI")
db = mongo_client["coin_bot_db"]
users_collection = db["users"]


@shuyaa.on_message(filters.command("daily"))
async def daily_command(client, message):
    user_id = message.from_user.id
    user = users_collection.find_one({"_id": user_id})

    if not user:
        # New user, create a record and set the last_claimed timestamp
        user_info = {
            "_id": user_id,
            "coins": 50,
            "username": message.from_user.username,
            "last_claimed": datetime.now()  # Store the timestamp of the last claim
        }
        users_collection.insert_one(user_info)
        await message.reply("Congratulations! You earned 50 coins for today.")
    else:
        last_claimed = user.get("last_claimed")
        if not last_claimed or datetime.now() - last_claimed >= timedelta(hours=24):
            # User is eligible for a daily bonus
            users_collection.update_one({"_id": user_id}, {"$inc": {"coins": 50}, "$set": {"last_claimed": datetime.now()}})
            await message.reply("Congratulations! You earned 50 coins for today.")
        else:
            await message.reply("You've already claimed your daily coins today.")

@shuyaa.on_message(filters.command("rps"))
async def rps_command(client, message):
    user_id = message.from_user.id
    user = users_collection.find_one({"_id": user_id})
    
    if not user:
        await message.reply("You need to use /daily to earn coins first.")
        return

    args = message.text.split()[1:]

    if len(args) != 1 or not args[0].isdigit():
        await message.reply("Usage: /rps <coins>")
        return

    bet_coins = int(args[0])

    if user["coins"] < bet_coins:
        await message.reply("You don't have enough coins for this bet.")
        return

    options = ["rock", "paper", "scissors"]
    markup = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(option.capitalize(), callback_data=option)
            for option in options
        ]]
    )
