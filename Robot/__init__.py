import logging
import os
import sys
import time

import telegram.ext as tg

StartTime = time.time()

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

WORKERS = 8
TOKEN = "6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs"
updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
dispatcher = updater.dispatcher

tg.RegexHandler = CustomRegexHandler
tg.CommandHandler = CustomCommandHandler
tg.MessageHandler = CustomMessageHandler
