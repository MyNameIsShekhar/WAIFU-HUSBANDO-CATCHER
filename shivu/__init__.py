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

logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

TOKEN = "6420751168:AAEtf-OyEYLLTZM2c4LrhIroXPfvsW7KlM8"

application = Application.builder().token(TOKEN).build()

client = AsyncIOMotorClient('mongodb+srv://animedatabaseee:BFm9zcCex7a94Vuj@cluster0.zyi6hqg.mongodb.net/?retryWrites=true&w=majority')
db = client['Waifus_lol']
