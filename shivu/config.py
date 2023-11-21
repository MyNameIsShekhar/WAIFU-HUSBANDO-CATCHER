class Config(object):
    LOGGER = True

    TOKEN = ""  #Bot Token.. @BotFather 
    MONGO_DB_URI = "" #if u don't know how to get.. then search on YouTube
    OWNER_ID = 6765826972
    GROUP_ID = -1001992659529
    SUPPORT_CHAT = "" # add ur Support Group username Without @
    PHOTO_URL = []
    SUDO_USERS = []


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
