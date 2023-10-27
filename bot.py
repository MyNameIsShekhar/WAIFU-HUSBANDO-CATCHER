from telethon import TelegramClient, events
from motor.motor_asyncio import AsyncIOMotorClient
import random

# Create instances of TelegramClient and Motor's AsyncIOMotorClient

api_id = '24427150'
api_hash = '9fcc60263a946ef550d11406667404fa'
bot_token = '6794007851:AAFOj7qlMXlyRU4GlNqjVtO-5snYvu6-cwc'

app = TelegramClient('my_session', api_id, api_hash)
app.start(bot_token=bot_token)

client = AsyncIOMotorClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
db = client['Waifus_lol']
#Your collections
user_totals_collection = db['user_totals_lmaoooo']
collection = db['anime_characters_lol']
locks = {}
# Your other global variables here...

@app.on(events.NewMessage())
async def message_counter(event):
    chat_id = str(event.chat_id)

    # Get or create a lock for this chat
    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    # Use the lock to ensure that only one instance of this function can run at a time for this chat
    async with lock:
        # Get message frequency and counter for this chat from the database
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get('message_frequency', 10)
            message_counter = chat_frequency.get('message_counter', 0)
        else:
            # Default to 20 messages if not set
            message_frequency =10
            message_counter = 0

        # Increment counter for this chat
        message_counter += 1

        # Send image after every message_frequency messages
        if message_counter % message_frequency == 0:
            await send_image(event)
            # Reset counter for this chat
            message_counter = 0

        # Update counter in the database
        await user_totals_collection.update_one(
            {'chat_id': chat_id},
            {'$set': {'message_counter': message_counter}},
            upsert=True
        )

async def send_image(event):
    chat_id = event.chat_id

    # Get all characters
    all_characters = [doc async for doc in collection.find({})]
    
    # Initialize sent characters list for this chat if it doesn't exist
    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    # Reset sent characters list if all characters have been sent
    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    # Select a random character that hasn't been sent yet
    character = random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])

    # Add character to sent characters list and set as last sent character
    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    # Reset first correct guess when a new character is sent
    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    # Send image with caption
    await app.send_file(
        event.chat_id,
        file=character['img_url'],
        caption="Use /Guess Command And.. Guess This Character Name.."
    )


app.run_until_disconnected()
