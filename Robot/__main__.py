import importlib
import re
import time
from platform import python_version as y
from sys import argv


from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown
from Robot import (
    
    
    TOKEN,
    
    dispatcher,
    
    updater,
)


                        
            

def main():
    
    updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    
    updater.idle()


if __name__ == "__main__":
    
    main()
