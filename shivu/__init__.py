import os
import telegram.ext as tg
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

OWNER_ID = ["5715764478", "6765826972"]
sudo_users = ["5715764478", "6765826972"]
GROUP_ID = -1001931513350
TOKEN = "6840530499:AAFEKebd8wQnVwLoTGPP6YDNZGLC7W16Lkc"
mongo_url = "mongodb+srv://shuyaashivu:9fcc60263a946ef550d11406667404fa@cluster0.ikub9lo.mongodb.net/?retryWrites=true&w=majority"
PHOTO_URL = "https://telegra.ph/file/f700d0bfe17a7c3ebe096.jpg", "https://telegra.ph/file/143eb04f0527c711dd839.jpg"
SUPPORT_CHAT = "Collect_em_support"
UPDATE_CHAT = "Collect_em_support"
BOT_USERNAME = "Collect_Em_AllBot"

application = Application.builder().token(TOKEN).build()

client = AsyncIOMotorClient(mongo_url)
db = client['Character_catcher']
collection = db['anime_characters_lol']
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']



