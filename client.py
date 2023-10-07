import logging
import os
import sys
import time
import telegram.ext as tg

WORKERS = 8

TOKEN = "6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs"

updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
dispatcher = updater.dispatcher
