
from pyrogram import Client, filters
from telegraph import upload_file
from pymongo import MongoClient
from bson.objectid import ObjectId
import os


api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6656458442:AAGJ1nKC2qil9SMU3NbElluHSmHJrN8oZsg'

app = Client("my_account", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


client = MongoClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')


lol = client['jay shree ram']
db = lol['loool']


@app.on_message(filters.command("upload") & filters.reply & filters.photo)
async def upload(client, message):
    if len(message.command) < 3:
        await message.reply_text("Please provide both character name and anime name.")
        return

    character_name = message.command[1].replace("-", " ")
    anime = message.command[2].replace("-", " ")

    photo = await app.download_media(message=message.reply_to_message, file_name="temp.jpg")
    telegraph_url = upload_file(photo)[0]
    os.remove(photo)

    unique_id = str(ObjectId())
    data = {
        "_id": unique_id,
        "character_name": character_name,
        "anime": anime,
        "url": telegraph_url
    }

    if db.find_one({"anime": anime}):
        db.update_one({"anime": anime}, {"$push": {"characters": data}})
    else:
        db.insert_one(data)

    await app.send_photo(
        chat_id='-1001670772912',
        photo=telegraph_url,
        caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n<b>ID:</b> {unique_id}\nAdded by <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>',
        parse_mode='HTML'
    )

app.run()


