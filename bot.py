# A Simple Heroku Bot to Echo the Message, the user sends to it.
# Here I used handlers, You can also use the Decorators, The steps are same.

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler

app = Client(
    "YOUR_SESSION_NAME",
    bot_token="YOUR_BOT_TOKEN",
    api_id="YOUR_API_ID",
    api_hash="YOUR_API_HASH"
)

# sends back the message you sent to the bot.
def echobot(client, message):
    message.reply_text(message.text)

def main():
    app.add_handler(MessageHandler(echobot, filters.text))


app.run(main())
