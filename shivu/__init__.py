import os
import telegram.ext as tg
import logging  
from pyrogram import Client 
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

OWNER_ID = 6765826972
sudo_users = ["6765826972", "6046482147"]
GROUP_ID = -100
TOKEN = ""
mongo_url = ""
PHOTO_URL = "", ""
SUPPORT_CHAT = "Collect_em_support"
UPDATE_CHAT = "Collect_em_support"
BOT_USERNAME = "Collect_Em_AllBot"
CHARA_CHANNEL_ID = -100
api_id = 
api_hash = ""


application = Application.builder().token(TOKEN).build()
shivuu = Client("Shivu", api_id, api_hash, bot_token=TOKEN)
client = AsyncIOMotorClient(mongo_url)
db = client['Character_catcher']
collection = db['anime_characters_lol']
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']



