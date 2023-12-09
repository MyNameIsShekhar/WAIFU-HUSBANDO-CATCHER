import logging  

from pyrogram import Client 

from telegram.ext import Application
from motor.motor_asyncio import AsyncIOMotorClient

from shivu.config import *

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

OWNER_ID = OWNER_ID
sudo_users = sudo_users
GROUP_ID = GROUP_ID
TOKEN = TOKEN
mongo_url = mongo_url
PHOTO_URL = PHOTO_URL
SUPPORT_CHAT = SUPPORT_CHAT
UPDATE_CHAT = UPDATE_CHAT
BOT_USERNAME = BOT_USERNAME
CHARA_CHANNEL_ID = CHARA_CHANNEL_ID
api_id = api_id
api_hash = api_hash


application = Application.builder().token(TOKEN).build()
shivuu = Client("Shivu", api_id, api_hash, bot_token=TOKEN)
client = AsyncIOMotorClient(mongo_url)
db = client['Character_catcher']
collection = db['anime_characters']
user_totals_collection = db['user_totals']
user_collection = db["user_collection"]
group_user_totals_collection = db['group_user_total']
top_global_groups_collection = db['top_global_groups']
pm_users = db['total_pm_users']
