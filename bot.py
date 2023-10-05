from pyrogram import Client, filters
from pymongo import MongoClient
import random

TOKEN = '6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs'
client = MongoClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')
db = client.get_database('test')
collection = db.get_collection('images')

app = Client("my_bot", bot_token=TOKEN, api_id=24427150, api_hash="9fcc60263a946ef550d11406667404fa")


@app.on_message(filters.command("upload"))
def upload(client, message):
    if message.reply_to_message and message.reply_to_message.photo:
        file_id = message.reply_to_message.photo.file_id
        image_name = message.text.split()[1]
        collection.insert_one({'file_id': file_id, 'name': image_name})

@app.on_message(filters.group)
def send_image(client, message):
    count = collection.count_documents({})
    if count % 10 == 0:
        doc = random.choice(list(collection.find()))
        app.send_photo(message.chat.id, doc['file_id'], caption="Guess the name and get coins")

@app.on_message(filters.command("guess"))
def guess(client, message):
    guess_name = message.text.split()[1]
    doc = collection.find_one({'name': guess_name})
    if doc:
        app.send_message(message.chat.id, f"{message.from_user.first_name} guessed the image correctly and got 5 coins")
        collection.delete_one({'_id': doc['_id']})

app.run()
