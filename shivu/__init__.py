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

OWNER_ID = ["5715764478", "6765826972"]
sudo_users = ["5715764478", "6765826972"]
GROUP_ID = -1001931513350
TOKEN = "6785717206:AAEzOZVgWP0D9H-TNo4b8HXfoe97ShUJ1B8"
mongo_url = "mongodb+srv://HaremDBBot:ThisIsPasswordForHaremDB@haremdb.swzjngj.mongodb.net/?retryWrites=true&w=majority"
PHOTO_URL = "https://graph.org/file/427df9b44c37f6d6a5eaa.jpg"
SUPPORT_CHAT = "botsupportx"
CHARA_CHANNEL_ID = "-1002064277119"
API_HASH = "750432c8e1b221f91fd2c93a92710093"
API_ID = 28122413
UPDATE_CHAT = "botsupportx"
BOT_USERNAME = "CatchEmWaifuBot"

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



