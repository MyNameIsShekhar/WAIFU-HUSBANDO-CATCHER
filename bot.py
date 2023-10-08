from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import random

# Setup MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
users = db["users"]

# Setup Pyrogram


api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6656458442:AAGJ1nKC2qil9SMU3NbElluHSmHJrN8oZsg'

app = Client("Lol", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


# After every 20 messages, the bot will send a question
message_counter = 0

# Questions, options and answers
questions = [
    {
        "question": "Question 1",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"],
        "answer": "Option 1",
        "image": "https://graph.org/file/cb384e79bc3ff2a36e1fa.jpg"
    },
    {
        "question": "Question 2",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"],
        "answer": "Option 2",
        "image": "https://graph.org/file/cb384e79bc3ff2a36e1fa.jpg"
    },
    # Add more questions here...
]

@app.on_message(filters.text & filters.group)
def handle_messages(client, message):
    global message_counter
    message_counter += 1

    if message_counter >= 20:
        message_counter = 0
        ask_question(message.chat.id)

def ask_question(chat_id):
    # Choose a random question
    question_data = random.choice(questions)
    
    # Create InlineKeyboardMarkup with options as InlineKeyboardButton
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(option, callback_data=option)] for option in question_data["options"]]
    )

    # Send the question and the options to the user
    app.send_photo(chat_id, question_data["image"], caption=question_data["question"], reply_markup=reply_markup)

@app.on_callback_query()
def handle_callback_query(client, callback_query):
    # Check if the answer is correct
    if callback_query.data == correct_answer:
        # If correct, delete the question and send a new message
        app.delete_messages(chat_id, callback_query.message.message_id)
        app.send_message(chat_id, f"@{callback_query.from_user.username}, you're correct! You get 5 coins.")

        # Add coins to the user's account in the database
        user = users.find_one({"username": callback_query.from_user.username})
        if user:
            users.update_one({"_id": user["_id"]}, {"$inc": {"coins": 5}})
        else:
            users.insert_one({"username": callback_query.from_user.username, "coins": 5})

app.run()
