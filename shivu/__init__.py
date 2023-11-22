import logging
import os
import sys
import telegram.ext as tg
import logging 
from shivu.config import Development as Config

from motor.motor_asyncio import AsyncIOMotorClient 
from telegram.ext import Application

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)


logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    )
    quit(1)

ENV = bool(os.environ.get("ENV", False))

if ENV:
    MONGO_DB_URI = os.environ.get("MONGO_DB_URI", None)
    TOKEN = os.environ.get("TOKEN", None)
    GROUP_ID = os.environ.get("GROUP_ID", None)
    SUDO_USERS = os.environ.get("SUDO_USERS", None)
    PHOTO_URL = os.environ.get("PHOTO_URL", None)
    OWNER_ID = os.environ.get("OWNER_ID", None)
    try:
        OWNER_ID = int(os.environ.get("OWNER_ID", None))
    except ValueError:
        raise Exception("Your OWNER_ID env variable is not a valid integer.")

else:
    
    TOKEN = Config.TOKEN
    SUPPORT_CHAT = Config.SUPPORT_CHAT
    MONGO_DB_URI = Config.MONGO_DB_URI
    GROUP_ID = Config.GROUP_ID
    SUDO_USERS = Config.SUDO_USERS
    OWNER_ID= Config.OWNER_ID 


application = Application.builder().token(TOKEN).build()

client = AsyncIOMotorClient(MONGO_DB_URI)
db = client['Character_catcher']
collection = db['anime_characters_lol']
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']

