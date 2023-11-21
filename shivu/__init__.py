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


TOKEN = "6315953148:AAHxTD8ZboAU30Brpw-ZJl20UcY88CnrEe8"
application = Application.builder().token(TOKEN).build()




client = AsyncIOMotorClient('mongodb+srv://shuyaashivu:9fcc60263a946ef550d11406667404fa@cluster0.ikub9lo.mongodb.net/?retryWrites=true&w=majority')
db = client['Character_catcher']
collection = db['anime_characters_lol']
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']

sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651','5813403535', '6393627898', '5952787198', '6614280216','6248411931','5216262234','1608353423']
