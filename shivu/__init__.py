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


TOKEN = "6670374898:AAENkuuAVF6Weivfm4bIw2H5MFcP43FxrbU"

application = Application.builder().token(TOKEN).build()

client = AsyncIOMotorClient('mongodb+srv://shuyaaaaa12:NvpoBuRp7MVPcAYA@cluster0.q2yycqx.mongodb.net/')
db = client['Character_catcher']

sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651','5813403535', '6393627898', '5952787198', '6614280216','6248411931','5216262234','1608353423']
