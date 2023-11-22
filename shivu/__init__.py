import os
import telegram.ext as tg
import logging 
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

OWNER_ID = os.getenv("OWNER_ID")
sudo_users = os.getenv("SUDO_USERS").split(',')
GROUP_ID = os.getnv("GROUP_ID")
TOKEN = os.getenv("TOKEN")
mongo_url = os.getenv("MONGO_URL")
PHOTO_URL = os.getenv("PHOTO_URL").split(',')
SUPPORT_CHAT = os.getnv("SUPPORT_CHAT")


application = Application.builder().token(TOKEN).build()


client = AsyncIOMotorClient(mongo_url)
db = client['Character_catcher']


