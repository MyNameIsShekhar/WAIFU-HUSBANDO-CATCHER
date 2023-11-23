import os
import telegram.ext as tg
from pyrogram import Client
import logging  
from telegram.ext import Application
from motor.motor_asyncio import AsyncIOMotorClient
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

OWNER_ID = os.getenv("OWNER_ID")
sudo_users = os.getenv("SUDO_USERS").split()
GROUP_ID = os.getenv("GROUP_ID")
TOKEN = os.getenv("TOKEN")
mongo_url = os.getenv("MONGO_URL")
PHOTO_URL = os.getenv("PHOTO_URL").split()
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT")
CHARA_CHANNEL_ID = os.getenv("CHARA_CHANNEL_ID")
API_HASH = os.getenv("API_HASH")
API_ID = os.getenv("API_ID")
UPDATE_CHAT = os.getenv("UPDATE_CHAT")

application = Application.builder().token(TOKEN).build()
shivuu = Client(
    "lmao",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    
    
)
client = AsyncIOMotorClient(mongo_url)
db = client['Character_catcher']
collection = db['anime_characters_lol']
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']



